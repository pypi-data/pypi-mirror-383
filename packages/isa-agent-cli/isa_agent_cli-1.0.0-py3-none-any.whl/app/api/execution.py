#!/usr/bin/env python3
"""
Execution Control API
Endpoints for managing execution state, resume, history, and rollback
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os
from datetime import datetime

from ..services.chat_service import ChatService
from ..components import MCPService, SessionService
from ..config import settings
from ..utils.logger import api_logger

# Pydantic models
class ResumeRequest(BaseModel):
    thread_id: str
    resume_data: Optional[dict] = None
    action: Optional[str] = "continue"  # continue, skip, modify, pause

class ResumeResponse(BaseModel):
    success: bool
    thread_id: str
    message: str
    next_step: Optional[str] = None

# Create router
router = APIRouter(prefix="/api/v1/agents/execution", tags=["execution_control"])

# Global chat service instance
chat_service: Optional[ChatService] = None

async def get_chat_service() -> ChatService:
    """Get or initialize ChatService instance"""
    global chat_service
    
    if not chat_service:
        # Initialize session manager
        session_service = SessionService()
        
        # Create chat service (MCPService will be initialized in the chat service)
        chat_service = ChatService(session_service=session_service)
        
        api_logger.info("🚀 ChatService initialized for Execution Control API")
    
    return chat_service

@router.post("/resume", response_model=ResumeResponse)
async def resume_execution(request: ResumeRequest):
    """Resume interrupted execution using LangGraph's native resume capabilities"""
    try:
        service = await get_chat_service()
        
        result = await service.resume_execution(
            thread_id=request.thread_id,
            action=request.action,
            resume_data=request.resume_data
        )
        
        return ResumeResponse(**result)
        
    except Exception as e:
        api_logger.error(f"❌ Resume execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Resume failed: {str(e)}")

@router.post("/resume-stream")
async def resume_execution_stream(request: ResumeRequest):
    """Resume interrupted execution with streaming response"""
    try:
        service = await get_chat_service()
        
        # SSE event generator for resume
        async def resume_sse_generator():
            try:
                # Resume and stream the continued execution
                async for event in service.resume_execution_stream(
                    thread_id=request.thread_id,
                    action=request.action,
                    resume_data=request.resume_data
                ):
                    # Convert to SSE format
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                
                # Send completion marker
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                api_logger.error(f"❌ Resume stream error: {e}")
                error_event = {
                    "type": "error",
                    "content": f"Resume error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
        
        # Return SSE streaming response
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
        
        # Only add CORS headers if not behind gateway
        if not os.getenv("BEHIND_GATEWAY", "").lower() == "true":
            headers.update({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            })
        
        return StreamingResponse(
            resume_sse_generator(),
            media_type="text/event-stream",
            headers=headers
        )
        
    except Exception as e:
        api_logger.error(f"❌ Resume stream setup error: {e}")
        raise HTTPException(status_code=500, detail=f"Resume stream setup failed: {str(e)}")

@router.get("/status/{thread_id}")
async def get_execution_status(thread_id: str):
    """Get current execution status for a thread"""
    try:
        service = await get_chat_service()
        
        status_info = await service.get_execution_status(thread_id)
        
        return {
            "thread_id": thread_id,
            **status_info
        }
        
    except Exception as e:
        api_logger.error(f"❌ Get execution status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/history/{thread_id}")
async def get_execution_history(thread_id: str, limit: int = 50):
    """Get execution history for a thread"""
    try:
        service = await get_chat_service()
        
        history_info = await service.get_execution_history(thread_id, limit)
        
        return {
            "thread_id": thread_id,
            **history_info
        }
        
    except Exception as e:
        api_logger.error(f"❌ Get execution history error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.post("/rollback/{thread_id}")
async def rollback_execution(thread_id: str, checkpoint_id: Optional[str] = None):
    """Rollback execution to a previous checkpoint"""
    try:
        service = await get_chat_service()
        
        rollback_result = await service.rollback_execution(thread_id, checkpoint_id)
        
        return {
            "thread_id": thread_id,
            **rollback_result
        }
        
    except Exception as e:
        api_logger.error(f"❌ Rollback execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")

@router.get("/health")
async def execution_health():
    """Health check for execution control service"""
    try:
        service = await get_chat_service()
        service_info = service.get_service_info()
        
        return {
            "status": "healthy",
            "service": "execution_control",
            "features": service_info.get("interrupt_features", {}),
            "graph_info": service_info.get("graph_info", {})
        }
        
    except Exception as e:
        api_logger.error(f"❌ Execution health check error: {e}")
        return {
            "status": "unhealthy",
            "service": "execution_control",
            "error": str(e)
        }