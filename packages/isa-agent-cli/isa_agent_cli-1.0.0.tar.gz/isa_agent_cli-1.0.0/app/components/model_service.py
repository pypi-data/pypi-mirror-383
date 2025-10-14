#!/usr/bin/env python3
"""
Model Service - High-performance ISA model abstraction

Core focus: Performance, Concurrency, Security, Stability
- Connection pooling and reuse
- Async/concurrent processing
- Error handling and timeouts
- Minimal overhead design
"""

import logging
import asyncio
import os
from typing import Dict, List, Any, Optional, Tuple
from langchain_core.messages import AIMessage

# Import isa_model directly (should be available in local mode)
from isa_model import ISAModelClient

# LangSmith tracing via centralized service
from .tracing_service import traceable_if_enabled
from ..utils.logger import api_logger

logger = api_logger  # Use centralized logger for visibility


class ModelService:
    """High-performance model service with connection reuse and error handling"""
    
    def __init__(self, isa_url: str = None, use_local: bool = True):
        if isa_url is None:
            from app.config import settings
            isa_url = settings.resolved_isa_api_url
        self.isa_url = isa_url
        self.use_local = use_local
        self._client: Optional[ISAModelClient] = None
        self._lock = asyncio.Lock()

    async def _get_client(self) -> ISAModelClient:
        """Thread-safe client singleton with connection reuse"""
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    if self.use_local:
                        # Local mode - direct AIFactory access (faster streaming)
                        self._client = ISAModelClient()
                        logger.info(f"ISA client initialized in LOCAL mode (direct AIFactory)")
                    else:
                        # HTTP API mode
                        self._client = ISAModelClient(service_endpoint=self.isa_url)
                        logger.info(f"ISA client initialized in HTTP mode: {self.isa_url}")
        return self._client

    def _serialize_messages(self, messages: List[Any]) -> str:
        """Convert LangChain messages to a string prompt for API mode

        The Model API expects input_data to be either str or dict, not a list.
        We convert messages to a formatted string that preserves context.
        """
        parts = []
        for msg in messages:
            # Handle LangChain message objects
            if hasattr(msg, 'type') and hasattr(msg, 'content'):
                role = msg.type
                content = msg.content

                # Format based on role
                if role == 'system':
                    parts.append(f"System: {content}")
                elif role == 'human' or role == 'user':
                    parts.append(f"User: {content}")
                elif role == 'ai' or role == 'assistant':
                    parts.append(f"Assistant: {content}")
                else:
                    parts.append(f"{role.capitalize()}: {content}")
            elif isinstance(msg, dict):
                # Handle dict format
                role = msg.get('role', 'user')
                content = msg.get('content', str(msg))
                parts.append(f"{role.capitalize()}: {content}")
            else:
                # Fallback: convert to string
                parts.append(f"User: {str(msg)}")

        return "\n\n".join(parts)
    
    @traceable_if_enabled
    async def call_model(
        self,
        messages: List[Any],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        timeout: float = 120.0
    ) -> Tuple[AIMessage, Optional[Dict[str, Any]]]:
        """
        High-performance model call with timeout and error handling
        
        Args:
            messages: LangChain messages
            tools: Optional tool definitions  
            model: Optional model override
            timeout: Request timeout in seconds
            
        Returns:
            (AIMessage, billing_info)
        """
        if not messages:
            raise ValueError("Messages required")

        client = await self._get_client()

        # Convert messages to JSON-serializable format if using API mode
        input_messages = messages if self.use_local else self._serialize_messages(messages)

        # Build args - minimal overhead
        args = {
            "input_data": input_messages,
            "task": "chat",
            "service_type": "text",
            "stream": False  # Use non-streaming for call_model (fixes gpt-5 org verification)
        }

        if tools:
            args["tools"] = tools

        if model:
            args["model"] = model

        if provider:
            args["provider"] = provider

        try:
            # Call with timeout protection
            response = await asyncio.wait_for(
                client.invoke(**args),
                timeout=timeout
            )
            
            if not response.get('success'):
                raise RuntimeError(f"Model call failed: {response}")

            # Handle non-streaming response (stream=False)
            if 'result' in response and not 'stream' in response:
                # Non-streaming response - result is AIMessage or dict with tool_calls
                result = response['result']
                billing = response.get('metadata', {}).get('billing', {})

                # Debug logging
                print(f"[DEBUG] model_service non-streaming result type: {type(result)}", flush=True)
                if isinstance(result, dict):
                    print(f"[DEBUG] result dict keys: {result.keys()}", flush=True)
                    print(f"[DEBUG] has tool_calls: {'tool_calls' in result}", flush=True)
                    if 'tool_calls' in result:
                        print(f"[DEBUG] tool_calls: {result['tool_calls']}", flush=True)

                if isinstance(result, AIMessage):
                    return result, billing
                elif isinstance(result, dict):
                    # Handle dict response with tool_calls (from ISA Model)
                    if 'tool_calls' in result:
                        ai_msg = AIMessage(
                            content=result.get('content', ''),
                            tool_calls=result['tool_calls']
                        )
                        print(f"[DEBUG] Created AIMessage with tool_calls: {ai_msg.tool_calls}", flush=True)
                        return ai_msg, billing
                    else:
                        return AIMessage(content=result.get('content', str(result))), billing
                else:
                    return AIMessage(content=str(result)), billing

            # Process stream efficiently (stream=True)
            if 'stream' in response:
                return await self._process_stream(response['stream'])
            else:
                return AIMessage(content="No stream or result in response"), None
                
        except asyncio.TimeoutError:
            logger.error(f"Model call timeout after {timeout}s")
            raise RuntimeError(f"Model timeout after {timeout}s")
        except Exception as e:
            logger.error(f"Model call failed: {e}")
            raise RuntimeError(f"Model error: {str(e)}")
    
    async def _process_stream(self, stream) -> Tuple[AIMessage, Optional[Dict[str, Any]]]:
        """Efficient stream processing with minimal memory overhead"""
        content_chunks = []
        final_result = None
        billing = None

        try:
            async for chunk in stream:
                if isinstance(chunk, str):
                    # String chunks are tokens
                    content_chunks.append(chunk)
                elif isinstance(chunk, dict):
                    # Final dict chunk contains metadata (result, billing, etc.)
                    final_result = chunk.get('result')
                    billing = chunk.get('billing')
                    break

            # Return final result if available, otherwise reconstruct from chunks
            if final_result:
                return final_result, billing
            elif content_chunks:
                return AIMessage(content=''.join(content_chunks)), billing
            else:
                return AIMessage(content="Empty response"), None

        except Exception as e:
            logger.error(f"Stream processing error: {e}")
            return AIMessage(content=f"Stream error: {str(e)}"), None
    
    @traceable_if_enabled
    async def stream_tokens(
        self,
        messages: List[Any],
        token_callback,
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        timeout: float = 120.0
    ) -> Tuple[AIMessage, Optional[Dict[str, Any]]]:
        """Stream tokens with callback for real-time processing"""
        if not messages:
            raise ValueError("Messages required for streaming")

        client = await self._get_client()

        # Convert messages to JSON-serializable format if using API mode
        input_messages = messages if self.use_local else self._serialize_messages(messages)

        args = {
            "input_data": input_messages,
            "task": "chat",
            "service_type": "text"
        }
        
        if tools:
            args["tools"] = tools

        if model:
            args["model"] = model

        if provider:
            args["provider"] = provider

        try:
            import time as time_module
            invoke_start = time_module.time()
            print(f"[TIMING] model_service_invoke_start | time={invoke_start}", flush=True)
            logger.info(f"[TIMING] model_service_invoke_start | time={invoke_start}")

            response = await asyncio.wait_for(
                client.invoke(**args),
                timeout=timeout
            )

            invoke_duration = int((time_module.time() - invoke_start) * 1000)
            print(f"[TIMING] model_service_invoke_complete | duration_ms={invoke_duration} | time={time_module.time()}", flush=True)
            logger.info(f"[TIMING] model_service_invoke_complete | duration_ms={invoke_duration}")

            if not response.get('success'):
                raise RuntimeError(f"Streaming call failed: {response}")

            if 'stream' in response:
                stream_start = time_module.time()
                result = await self._stream_with_callback(response['stream'], token_callback)
                stream_duration = int((time_module.time() - stream_start) * 1000)
                logger.info(f"[PERF] stream_with_callback completed in {stream_duration}ms")
                return result
            else:
                return AIMessage(content="No stream available"), None
                
        except asyncio.TimeoutError:
            logger.error(f"Streaming timeout after {timeout}s")
            raise RuntimeError(f"Streaming timeout after {timeout}s")
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            raise RuntimeError(f"Streaming error: {str(e)}")
    
    async def _stream_with_callback(self, stream, callback) -> Tuple[AIMessage, Optional[Dict[str, Any]]]:
        """
        Process stream with token-level callbacks

        Streams all tokens through callback for real-time display.
        Waits for complete response to get billing info and final result.
        """
        import time as time_module
        stream_start = time_module.time()

        content_chunks = []
        final_result = None
        billing = None
        first_token_received = False
        token_count = 0

        try:
            print(f"[STREAM_DEBUG] Starting stream iteration at {time_module.time()}", flush=True)
            logger.info(f"[STREAM_DEBUG] Starting stream iteration at {time_module.time()}")

            iteration_count = 0
            async for chunk in stream:
                iteration_count += 1

                # Log what type of chunk we received
                chunk_type = type(chunk).__name__
                if iteration_count == 1:
                    print(f"[STREAM_DEBUG] First chunk type: {chunk_type}, is_str={isinstance(chunk, str)}, is_dict={isinstance(chunk, dict)}", flush=True)
                    logger.info(f"[STREAM_DEBUG] First chunk type: {chunk_type}")

                # Log timing for first chunk
                if not first_token_received:
                    first_chunk_time = int((time_module.time() - stream_start) * 1000)
                    print(f"[PERF] First chunk received from stream iteration: {first_chunk_time}ms (type={chunk_type})", flush=True)
                    logger.info(f"[PERF] First chunk received from stream iteration: {first_chunk_time}ms")
                    first_token_received = True

                if isinstance(chunk, str):
                    token_count += 1
                    # Stream token immediately via callback
                    if callback:
                        callback({"token": chunk})
                    content_chunks.append(chunk)

                    # Log every 10th token to track progress
                    if token_count % 10 == 0:
                        print(f"[STREAM_DEBUG] Streamed {token_count} tokens so far", flush=True)
                        logger.info(f"[STREAM_DEBUG] Streamed {token_count} tokens so far")

                elif isinstance(chunk, dict):
                    # Final dict chunk contains metadata (result, billing, etc.)
                    print(f"[STREAM_DEBUG] Received final metadata chunk after {token_count} tokens", flush=True)
                    logger.info(f"[STREAM_DEBUG] Received final metadata chunk after {token_count} tokens")
                    final_result = chunk.get('result')
                    billing = chunk.get('billing')
                    break

            stream_duration = int((time_module.time() - stream_start) * 1000)
            print(f"[STREAM_DEBUG] Stream iteration complete: {token_count} tokens in {stream_duration}ms", flush=True)
            logger.info(f"[STREAM_DEBUG] Stream iteration complete: {token_count} tokens in {stream_duration}ms")

            # Return complete response with billing
            if final_result:
                return final_result, billing
            elif content_chunks:
                return AIMessage(content=''.join(content_chunks)), billing
            else:
                return AIMessage(content=""), None

        except Exception as e:
            logger.error(f"[STREAM_DEBUG] Callback streaming error: {e}", exc_info=True)
            return AIMessage(content=f"Callback error: {str(e)}"), None
    
    @traceable_if_enabled
    async def transcribe_audio(
        self,
        audio_file_path: str,
        timeout: float = 60.0
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using ISA model service
        
        Args:
            audio_file_path: Path to audio file
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with transcription result
        """
        if not audio_file_path:
            raise ValueError("Audio file path required")
        
        client = await self._get_client()
        
        try:
            # Call ISA audio transcription service
            response = await asyncio.wait_for(
                client.invoke(
                    input_data=audio_file_path,
                    task="transcribe",
                    service_type="audio"
                ),
                timeout=timeout
            )
            
            logger.info(f"Audio transcription response: {response}")
            
            if not response.get('success'):
                raise RuntimeError(f"Audio transcription failed: {response}")
                
            return response
                
        except asyncio.TimeoutError:
            logger.error(f"Audio transcription timeout after {timeout}s")
            raise RuntimeError(f"Audio transcription timeout after {timeout}s")
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise RuntimeError(f"Audio transcription error: {str(e)}")

    @traceable_if_enabled
    async def health_check(self) -> bool:
        """Quick health check for service availability"""
        try:
            client = await self._get_client()
            result = await asyncio.wait_for(client.health_check(), timeout=5.0)
            return result.get('status') == 'healthy'
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    def close(self):
        """Clean shutdown"""
        if self._client:
            try:
                self._client.close()
            except:
                pass
            self._client = None
            logger.info("Model service closed")


# Global singleton for performance
_model_service: Optional[ModelService] = None
_service_lock = asyncio.Lock()


async def get_model_service(isa_url: str = None, use_local: bool = None) -> ModelService:
    """Get thread-safe singleton model service"""
    global _model_service

    if _model_service is None:
        async with _service_lock:
            if _model_service is None:
                # Auto-detect use_local from config if not specified
                if use_local is None:
                    from app.config import settings
                    use_local = settings.isa_mode == "local"
                    logger.info(f"Auto-detected ISA_MODE from config: {settings.isa_mode} -> use_local={use_local}")

                _model_service = ModelService(isa_url, use_local=use_local)
                logger.info(f"Global ModelService initialized (local={use_local})")

    return _model_service