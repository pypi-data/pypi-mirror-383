#!/usr/bin/env python3
"""
Sync Mode Handler for isA Agent CLI
Handles proper parsing of SSE events followed by final JSON response
"""

import json
import requests
from typing import Dict, Any, List
from datetime import datetime


class SyncResponseHandler:
    """Handles synchronous mode responses that come as SSE events + final JSON"""
    
    def __init__(self, api_base_url: str, api_key: str):
        self.api_base_url = api_base_url
        self.api_key = api_key
    
    async def handle_sync_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sync mode: process SSE events and extract final JSON response"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/agents/chat",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=120,  # Increased timeout for sync mode
                stream=True
            )
            response.raise_for_status()
            
            # Process SSE events and collect final response
            final_response = None
            response_content = ""
            events_processed = 0
            tool_results = []
            
            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.startswith('data: '):
                    continue
                
                data_part = line[6:]  # Remove 'data: ' prefix
                
                if data_part == '[DONE]':
                    break
                
                try:
                    event = json.loads(data_part)
                    events_processed += 1
                    
                    # Collect response content from token events
                    if event.get('type') == 'content.token':
                        response_content += event.get('content', '')
                    
                    # Look for complete response content (final response from response node)
                    elif event.get('type') == 'content.complete':
                        # ResponseNode provides the final formatted response
                        node_type = event.get('metadata', {}).get('node', '')
                        if node_type in ['AIMessage', 'format_response']:
                            complete_content = event.get('content', '')
                            if complete_content:
                                response_content = complete_content
                    
                    # Collect tool results
                    elif event.get('type') == 'tool_result_msg':
                        tool_results.append(event.get('content', ''))
                    
                    # Check for session end to finalize
                    elif event.get('type') == 'session.end':
                        final_response = {
                            "success": True,
                            "response": response_content,
                            "session_id": event.get('session_id'),
                            "tool_results": tool_results,
                            "events_count": events_processed,
                            "timestamp": event.get('timestamp')
                        }
                        
                except json.JSONDecodeError:
                    # Skip malformed JSON events
                    continue
            
            # If we didn't get a final response, construct one
            if not final_response:
                final_response = {
                    "success": True,
                    "response": response_content or "Response completed successfully",
                    "session_id": payload.get('session_id'),
                    "tool_results": tool_results,
                    "events_count": events_processed,
                    "timestamp": datetime.now().isoformat()
                }
            
            return final_response
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {e}",
                "response": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Sync mode error: {e}",
                "response": ""
            }
    
    async def handle_sync_multimodal_response(self, form_data: Dict[str, Any], files: List[tuple]) -> Dict[str, Any]:
        """Handle sync mode for multimodal file uploads"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/agents/chat/multimodal",
                data=form_data,
                files=files,
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                timeout=120,
                stream=True
            )
            response.raise_for_status()
            
            # Use the same SSE processing logic
            return await self._process_sse_to_json(response)
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Multimodal request failed: {e}",
                "response": ""
            }
    
    async def _process_sse_to_json(self, response) -> Dict[str, Any]:
        """Common SSE to JSON processing logic"""
        final_response = None
        response_content = ""
        events_processed = 0
        tool_results = []
        
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith('data: '):
                continue
            
            data_part = line[6:]  # Remove 'data: ' prefix
            
            if data_part == '[DONE]':
                break
            
            try:
                event = json.loads(data_part)
                events_processed += 1
                
                # Collect response content from token events
                if event.get('type') == 'content.token':
                    response_content += event.get('content', '')
                
                # Look for complete response content
                elif event.get('type') == 'content.complete':
                    node_type = event.get('metadata', {}).get('node', '')
                    if node_type in ['AIMessage', 'format_response']:
                        complete_content = event.get('content', '')
                        if complete_content:
                            response_content = complete_content
                
                # Collect tool results
                elif event.get('type') == 'tool_result_msg':
                    tool_results.append(event.get('content', ''))
                
                # Check for session end
                elif event.get('type') == 'session.end':
                    final_response = {
                        "success": True,
                        "response": response_content,
                        "session_id": event.get('session_id'),
                        "tool_results": tool_results,
                        "events_count": events_processed,
                        "timestamp": event.get('timestamp')
                    }
                    
            except json.JSONDecodeError:
                continue
        
        if not final_response:
            final_response = {
                "success": True,
                "response": response_content or "Response completed successfully",
                "tool_results": tool_results,
                "events_count": events_processed,
                "timestamp": datetime.now().isoformat()
            }
        
        return final_response