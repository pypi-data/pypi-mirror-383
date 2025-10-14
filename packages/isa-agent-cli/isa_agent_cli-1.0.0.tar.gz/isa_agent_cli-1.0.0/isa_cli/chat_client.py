#!/usr/bin/env python3
"""
Chat Client for isA Agent CLI
Handles API communication for both streaming and sync modes
"""

import json
import requests
import httpx
from typing import Dict, Any, List, AsyncIterator
from pathlib import Path

from .sync_handler import SyncResponseHandler


class ChatClient:
    """Handles communication with the isA Agent API"""
    
    def __init__(self, api_base_url: str, api_key: str, timeout: int = 60):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.timeout = timeout
        
        # Initialize sync handler
        self.sync_handler = SyncResponseHandler(api_base_url, api_key)
        
        # Initialize async client for streaming
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            follow_redirects=True
        )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def send_message(self, message: str, user_id: str, session_id: str, 
                          output_format: str = "stream"):
        """Send a text message to the agent"""
        payload = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            "output_format": output_format if output_format == "json" else None
        }
        
        if output_format == "json":
            # Synchronous mode - handle SSE events then extract final JSON
            result = await self.sync_handler.handle_sync_response(payload)
            yield result  # Yield the result as a single event for consistency
        else:
            # Streaming mode - return async generator
            async for event in self._handle_streaming_response(payload):
                yield event
    
    async def send_message_with_files(self, message: str, file_paths: List[str], 
                                    user_id: str, session_id: str,
                                    output_format: str = "stream"):
        """Send a message with file attachments"""
        files = []
        file_data = []
        
        try:
            # Prepare files for upload
            for file_path in file_paths:
                path = Path(file_path)
                if not path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                with open(path, 'rb') as f:
                    file_content = f.read()
                    file_data.append({
                        "filename": path.name,
                        "content": file_content,
                        "size": len(file_content)
                    })
                    files.append(('files', (path.name, file_content, 'application/octet-stream')))
            
            # Prepare form data
            form_data = {
                'message': message,
                'user_id': user_id,
                'session_id': session_id,
                'file_metadata': json.dumps([{
                    "filename": fd["filename"],
                    "size": fd["size"]
                } for fd in file_data])
            }
            
            if output_format == "json":
                form_data['output_format'] = output_format
                # Synchronous mode with file upload
                result = await self.sync_handler.handle_sync_multimodal_response(form_data, files)
                yield result  # Yield the result as a single event for consistency
            else:
                # Streaming mode with file upload - return async generator
                async for event in self._handle_streaming_multipart_response(form_data, files):
                    yield event
                
        except Exception as e:
            yield {
                "type": "error",
                "content": f"File upload error: {e}",
                "success": False,
                "error": str(e)
            }
    
    async def _handle_streaming_response(self, payload: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """Handle SSE streaming response"""
        response_buffer = []
        events_received = []
        final_response = None
        
        try:
            # Use requests for streaming (httpx has connection issues)
            response = requests.post(
                f"{self.api_base_url}/api/v1/agents/chat",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                },
                stream=True,
                timeout=(30, 120)  # 30s connect, 120s read
            )
            
            response.raise_for_status()
            
            # Process SSE events
            for event in self._process_sse_stream(response):
                events_received.append(event)
                yield event  # Yield for real-time processing
                
                # Collect response content
                if event.get('type') == 'content.token':
                    response_buffer.append(event.get('content', ''))
                elif event.get('type') == 'content.complete':
                    complete_content = event.get('content', '')
                    if complete_content:
                        final_response = complete_content
                
        except Exception as e:
            yield {
                "type": "error",
                "content": f"Chat processing error: {e}",
                "timestamp": "",
                "session_id": payload.get('session_id', ''),
                "success": False
            }
    
    async def _handle_streaming_multipart_response(self, form_data: Dict[str, Any], 
                                                  files: List[tuple]) -> AsyncIterator[Dict[str, Any]]:
        """Handle SSE streaming response for multipart file uploads"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/agents/chat/multimodal",
                data=form_data,
                files=files,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "text/event-stream"
                },
                stream=True,
                timeout=(30, 180)  # Longer timeout for file uploads
            )
            
            response.raise_for_status()
            
            # Process SSE events
            for event in self._process_sse_stream(response):
                yield event
                
        except Exception as e:
            yield {
                "type": "error",
                "content": f"Multimodal upload error: {e}",
                "timestamp": "",
                "session_id": form_data.get('session_id', ''),
                "success": False
            }
    
    def _process_sse_stream(self, response):
        """Process Server-Sent Events stream"""
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith('data: '):
                continue
            
            data_part = line[6:]  # Remove 'data: ' prefix
            
            if data_part == '[DONE]':
                break
            
            try:
                event = json.loads(data_part)
                yield event
            except json.JSONDecodeError:
                # Skip malformed events
                continue
    
    async def check_health(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = requests.get(
                f"{self.api_base_url}/health",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }