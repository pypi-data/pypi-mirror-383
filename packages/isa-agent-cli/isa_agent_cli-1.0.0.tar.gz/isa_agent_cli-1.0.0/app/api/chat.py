#!/usr/bin/env python3
"""
Chat API - Clean and simple
"""

import json
import os
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Depends, Form, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from ..services.chat_service import ChatService
from ..components import SessionService
from ..components.multimodal_processor import MultimodalProcessor
from ..config import settings
from ..utils.logger import api_logger
from .auth import require_chat_permission


class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: str
    prompt_name: Optional[str] = None
    prompt_args: Optional[dict] = None
    # Graph selection fields (NEW)
    graph_type: Optional[str] = None  # Explicit graph type selection
    auto_select_graph: Optional[bool] = True  # Auto-select based on task
    # Intelligent mode configuration
    confidence_threshold: Optional[float] = 0.7
    proactive_predictions: Optional[dict] = None
    # Hardware integration fields
    device_context: Optional[dict] = None
    media_files: Optional[List[dict]] = None
    sensor_data: Optional[dict] = None
    trigger_type: Optional[str] = "user_request"
    # Output format control
    output_format: Optional[str] = None  # "json" for structured output, None for streaming


class ResumeRequest(BaseModel):
    user_id: str
    session_id: str
    resume_value: Optional[dict] = None  # Authorization result or other resume data
    prompt_name: Optional[str] = None
    prompt_args: Optional[dict] = None
    # Intelligent mode configuration
    confidence_threshold: Optional[float] = 0.7
    proactive_predictions: Optional[dict] = None


router = APIRouter(prefix="/api/v1/agents/chat", tags=["chat"])


# Thread-safe singleton chat service
class ChatServiceSingleton:
    _instance: Optional[ChatService] = None
    _lock = None
    
    @classmethod
    async def get_instance(cls) -> ChatService:
        """Thread-safe singleton pattern for ChatService"""
        if cls._instance is None:
            if cls._lock is None:
                import asyncio
                cls._lock = asyncio.Lock()
            
            async with cls._lock:
                if cls._instance is None:
                    session_service = SessionService()
                    cls._instance = ChatService(session_service=session_service)
                    api_logger.info("ChatService initialized for API")
        
        return cls._instance


async def get_chat_service() -> ChatService:
    """Get ChatService instance (thread-safe)"""
    return await ChatServiceSingleton.get_instance()


@router.post("")
async def chat_endpoint(
    request: Request,
    api_key_info: dict = Depends(require_chat_permission)
):
    """Chat endpoint - streaming SSE mode with optional JSON-formatted final response"""
    try:
        service = await get_chat_service()
        
        # Parse JSON request
        try:
            json_data = await request.json()
            message = json_data.get("message")
            session_id = json_data.get("session_id")
            user_id = json_data.get("user_id")
            prompt_name = json_data.get("prompt_name")
            prompt_args = json_data.get("prompt_args", {})
            # Parse graph selection fields (NEW)
            graph_type = json_data.get("graph_type")
            auto_select_graph = json_data.get("auto_select_graph", True)
            # Parse intelligent mode configuration
            confidence_threshold = json_data.get("confidence_threshold", 0.7)
            proactive_predictions = json_data.get("proactive_predictions")
            # Parse hardware integration fields
            device_context = json_data.get("device_context")
            media_files = json_data.get("media_files", [])
            sensor_data = json_data.get("sensor_data")
            trigger_type = json_data.get("trigger_type", "user_request")
            # Parse output format - "json" for structured final response, None for plain text
            output_format = json_data.get("output_format")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        
        # Validate required parameters
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")
        
        # Structured logging with metrics
        import time
        request_start = time.time()

        api_logger.info(
            f"[PHASE:API] chat_request_received | "
            f"session_id={session_id} | "
            f"user_id={user_id} | "
            f"message='{message[:100]}{'...' if len(message) > 100 else ''}' | "
            f"message_length={len(message)} | "
            f"graph_type={graph_type or 'auto'} | "
            f"auto_select={auto_select_graph} | "
            f"has_media={bool(media_files)} | "
            f"prompt_name={prompt_name} | "
            f"output_format={output_format}"
        )

        # Extract auth token from request headers
        auth_token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header[7:]  # Remove "Bearer " prefix
        
        # SSE generator for streaming mode
        async def sse_event_generator():
            try:
                # Track time to first event
                service_start = time.time()
                api_logger.info(
                    f"[PHASE:API] sse_generator_start | "
                    f"session_id={session_id} | "
                    f"user_id={user_id} | "
                    f"time_from_request_ms={int((service_start - request_start) * 1000)}"
                )

                # Log all parameters being passed to service
                api_logger.info(
                    f"[PHASE:API] service_execute_params | "
                    f"session_id={session_id} | "
                    f"user_id={user_id} | "
                    f"graph_type={graph_type} | "
                    f"auto_select_graph={auto_select_graph} | "
                    f"has_prompt={bool(prompt_name)} | "
                    f"output_format={output_format} | "
                    f"has_media={bool(media_files)}"
                )

                event_count = 0
                first_event_received = False
                async for event in service.execute(
                    user_input=message,
                    session_id=session_id,
                    user_id=user_id,
                    prompt_name=prompt_name,
                    prompt_args=prompt_args,
                    auth_token=auth_token,
                    graph_type=graph_type,  # NEW
                    auto_select_graph=auto_select_graph,  # NEW
                    confidence_threshold=confidence_threshold,
                    proactive_predictions=proactive_predictions,
                    device_context=device_context,
                    media_files=media_files,
                    sensor_data=sensor_data,
                    trigger_type=trigger_type,
                    output_format=output_format  # Pass to nodes for final response formatting
                ):
                    # Log first event received from service
                    if not first_event_received:
                        first_event_time = time.time()
                        api_logger.info(
                            f"[PHASE:API] first_event_from_service | "
                            f"session_id={session_id} | "
                            f"user_id={user_id} | "
                            f"event_type={event.get('type')} | "
                            f"time_from_service_start_ms={int((first_event_time - service_start) * 1000)}"
                        )
                        first_event_received = True

                    event_count += 1
                    event_type = event.get('type', 'unknown')

                    # Log important event types
                    if event_type in ['thinking', 'token', 'tool_calls', 'node_update', 'content']:
                        api_logger.debug(
                            f"[PHASE:API] event_yielded | "
                            f"session_id={session_id} | "
                            f"event_num={event_count} | "
                            f"event_type={event_type} | "
                            f"has_content={bool(event.get('content'))}"
                        )

                    # Safe JSON serialization
                    try:
                        event_json = json.dumps(event, ensure_ascii=False, default=str)
                    except Exception as serialize_error:
                        api_logger.warning(
                            f"[PHASE:API] event_serialization_error | "
                            f"session_id={session_id} | "
                            f"event_type={event_type} | "
                            f"error={str(serialize_error)[:100]}"
                        )
                        # Fallback: convert problematic values to strings
                        safe_event = {}
                        for key, value in event.items():
                            try:
                                json.dumps(value)
                                safe_event[key] = value
                            except:
                                safe_event[key] = str(value)
                        event_json = json.dumps(safe_event, ensure_ascii=False)

                    yield f"data: {event_json}\n\n"
                
                yield "data: [DONE]\n\n"

                # Log successful completion with detailed stats
                duration_ms = int((time.time() - request_start) * 1000)
                api_logger.info(
                    f"[PHASE:API] chat_complete | "
                    f"session_id={session_id} | "
                    f"user_id={user_id} | "
                    f"total_events={event_count} | "
                    f"duration_ms={duration_ms} | "
                    f"status=success"
                )

            except Exception as e:
                duration_ms = int((time.time() - request_start) * 1000)
                api_logger.error(
                    f"chat_error | "
                    f"session_id={session_id} | "
                    f"user_id={user_id} | "
                    f"duration_ms={duration_ms} | "
                    f"error={type(e).__name__} | "
                    f"message={str(e)[:200]}",
                    exc_info=True
                )
                error_event = {
                    "type": "error",
                    "content": f"Processing error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
        
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
        
        # Only add CORS headers if not behind gateway
        if not os.getenv("BEHIND_GATEWAY", "").lower() == "true":
            headers["Access-Control-Allow-Origin"] = "*"
        
        return StreamingResponse(
            sse_event_generator(),
            media_type="text/event-stream",
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        from ..core.errors.error_handler import handle_api_error
        raise handle_api_error("chat", e)


# /sync endpoint removed - functionality merged into main chat endpoint with output_format="json"


@router.post("/resume")
async def resume_endpoint(
    request: Request,
    api_key_info: dict = Depends(require_chat_permission)
):
    """Resume interrupted chat execution"""
    try:
        service = await get_chat_service()
        
        # Parse JSON request
        try:
            json_data = await request.json()
            session_id = json_data.get("session_id")
            user_id = json_data.get("user_id")
            resume_value = json_data.get("resume_value")
            prompt_name = json_data.get("prompt_name")
            prompt_args = json_data.get("prompt_args", {})
            # Parse intelligent mode configuration for resume
            confidence_threshold = json_data.get("confidence_threshold", 0.7)
            proactive_predictions = json_data.get("proactive_predictions")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        
        # Validate required parameters
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")
        
        api_logger.info(f"Resume request from user: {user_id}, session: {session_id}")
        
        # Extract auth token from request headers
        auth_token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header[7:]  # Remove "Bearer " prefix
        
        # SSE generator for resume
        async def resume_sse_generator():
            try:
                async for event in service.resume_execution(
                    session_id=session_id,
                    user_id=user_id,
                    resume_value=resume_value,
                    prompt_name=prompt_name,
                    prompt_args=prompt_args,
                    auth_token=auth_token,
                    confidence_threshold=confidence_threshold,
                    proactive_predictions=proactive_predictions
                ):
                    # Safe JSON serialization (same as chat endpoint)
                    try:
                        event_json = json.dumps(event, ensure_ascii=False, default=str)
                    except Exception:
                        # Fallback: convert problematic values to strings
                        safe_event = {}
                        for key, value in event.items():
                            try:
                                json.dumps(value)
                                safe_event[key] = value
                            except:
                                safe_event[key] = str(value)
                        event_json = json.dumps(safe_event, ensure_ascii=False)
                    
                    yield f"data: {event_json}\n\n"
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                api_logger.error(f"Resume SSE generation error: {e}")
                error_event = {
                    "type": "error",
                    "content": f"Resume processing error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            resume_sse_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        from ..core.errors.error_handler import handle_api_error
        raise handle_api_error("chat_resume", e)


@router.post("/multimodal")
async def multimodal_chat_endpoint(
    request: Request,
    api_key_info: dict = Depends(require_chat_permission),
    message: Optional[str] = Form(None),
    user_id: str = Form(...),
    session_id: str = Form(...),
    prompt_name: Optional[str] = Form(None),
    prompt_args: Optional[str] = Form(None),  # JSON string
    confidence_threshold: Optional[float] = Form(0.7),
    proactive_predictions: Optional[str] = Form(None),  # JSON string
    audio: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """多模态聊天端点 - 支持文本、语音和文件上传"""
    try:
        service = await get_chat_service()
        
        # Extract auth token from request headers (moved early like normal chat endpoint)
        auth_token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header[7:]  # Remove "Bearer " prefix
        
        # 验证至少有一种输入
        if not message and not (audio and audio.filename) and not files:
            raise HTTPException(
                status_code=400, 
                detail="需要提供文字消息、语音文件或其他文件中的至少一种"
            )
        
        # 处理JSON字符串参数
        parsed_prompt_args = {}
        parsed_predictions = None
        
        try:
            if prompt_args:
                parsed_prompt_args = json.loads(prompt_args)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="prompt_args must be valid JSON")
        
        try:
            if proactive_predictions:
                parsed_predictions = json.loads(proactive_predictions)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="proactive_predictions must be valid JSON")
        
        # 处理多模态输入
        final_message = message or ""
        audio_text = ""
        file_content = ""
        
        if audio or files:
            processor = MultimodalProcessor(
                isa_url=settings.resolved_isa_api_url
                # storage_service_url will use Consul discovery by default
            )
            try:
                # 处理音频文件 (keep current audio processing)
                if audio and audio.filename:
                    api_logger.info(f"Processing audio file: {audio.filename}")
                    audio_result = await processor.process_audio_file(audio)
                    
                    if audio_result.get("success"):
                        audio_text = audio_result.get("text", "")
                        api_logger.info(f"Audio transcribed: {len(audio_text)} characters")
                    else:
                        api_logger.warning(f"Audio processing failed: {audio_result.get('error')}")
                
                # 处理其他文件 - 保存到MinIO并获取可访问的URL
                file_urls = []  # Store MinIO URLs for graph access
                file_metadata = []  # Store metadata for context
                
                if files:
                    # Process and store files to MinIO
                    storage_result = await processor.process_files_with_storage(
                        files=files,
                        user_id=user_id,
                        auth_token=auth_token,
                        organization_id=None  # Can be added later if needed
                    )
                    
                    if storage_result.get("success"):
                        # Extract file URLs and metadata from storage result
                        stored_files = storage_result.get("stored_files", [])
                        for file_info in stored_files:
                            file_urls.append(file_info.get("url", ""))
                            file_metadata.append({
                                "filename": file_info.get("filename", ""),
                                "content_type": file_info.get("content_type", ""),
                                "size": file_info.get("size", 0),
                                "url": file_info.get("url", ""),
                                "file_id": file_info.get("file_id", "")
                            })
                        
                        # Get summary for immediate context
                        file_content = storage_result.get("combined_content", "")
                        api_logger.info(
                            f"Files stored in MinIO: {len(stored_files)} files | "
                            f"URLs generated: {len(file_urls)} | "
                            f"Ready for analysis"
                        )
                    else:
                        file_content = f"文件处理出错: {storage_result.get('error', 'Unknown error')}"
                        api_logger.error(f"File processing with storage failed: {storage_result.get('error')}")
                
            finally:
                await processor.close()
        
        # 组合最终消息
        message_parts = []
        
        if final_message:
            message_parts.append(final_message)
        
        if audio_text:
            message_parts.append(f"\n\n[语音转录]:\n{audio_text}")
        
        if file_content:
            message_parts.append(f"\n\n[文件处理结果]:\n{file_content}")
        
        combined_message = "".join(message_parts).strip()
        
        if not combined_message:
            raise HTTPException(
                status_code=400, 
                detail="无法从提供的输入中提取有效内容"
            )
        
        api_logger.info(f"Multimodal chat request from user: {user_id}, session: {session_id}")
        api_logger.info(f"Final message length: {len(combined_message)} characters")
        
        # SSE generator
        async def multimodal_sse_generator():
            try:
                async for event in service.execute(
                    user_input=combined_message,
                    session_id=session_id,
                    user_id=user_id,
                    prompt_name=prompt_name,
                    prompt_args=parsed_prompt_args,
                    auth_token=auth_token,
                    # Pass file URLs and metadata for graph processing
                    media_files=file_metadata if file_metadata else None,
                    file_urls=file_urls if file_urls else None
                ):
                    # 添加多模态标识
                    if isinstance(event, dict):
                        event["multimodal"] = True
                        if audio_text:
                            event["audio_transcription"] = True
                    
                    # 安全的JSON序列化
                    try:
                        event_json = json.dumps(event, ensure_ascii=False, default=str)
                    except Exception as serialize_error:
                        # 回退策略
                        safe_event = {
                            "type": event.get("type", "unknown"),
                            "content": str(event.get("content", "")),
                            "timestamp": event.get("timestamp", ""),
                            "session_id": event.get("session_id", ""),
                            "multimodal": True
                        }
                        event_json = json.dumps(safe_event, ensure_ascii=False)
                    
                    yield f"data: {event_json}\n\n"
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                api_logger.error(f"Multimodal SSE generation error: {e}")
                error_event = {
                    "type": "error",
                    "content": f"多模态处理错误: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "multimodal": True
                }
                yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            multimodal_sse_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Multimodal chat endpoint error: {e}")
        from ..core.errors.error_handler import handle_api_error
        raise handle_api_error("multimodal_chat", e)



@router.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }