#!/usr/bin/env python3
"""
Session API for SmartAgent v3.0
Complete session lifecycle management for frontend applications
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path, Request, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..components.session_service import SessionService
from ..types.request_models import (
    SessionRequest, SessionHistoryRequest, SessionClearRequest
)
from ..types.response_models import BaseResponse
from ..utils.logger import api_logger

# Response Models
class SessionData(BaseModel):
    id: str
    user_id: str
    title: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    status: str = "active"
    summary: str = ""
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SessionListResponse(BaseResponse):
    sessions: List[SessionData]
    pagination: Dict[str, Any]

class SessionDetailResponse(BaseResponse):
    session: SessionData
    conversation_history: Optional[List[Dict]] = None
    stats: Optional[Dict] = None

class MessageData(BaseModel):
    id: str
    session_id: str
    role: str
    content: Dict[str, Any]
    timestamp: datetime
    token_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatHistoryResponse(BaseResponse):
    messages: List[MessageData]
    pagination: Dict[str, Any]

class SessionStatsResponse(BaseResponse):
    stats: Dict[str, Any]

# Create router
router = APIRouter(prefix="/api/v1/agents/sessions", tags=["sessions"])

# Global session manager instance
session_service: Optional[SessionService] = None

async def get_session_service() -> SessionService:
    """Get or initialize SessionService instance"""
    global session_service
    
    if not session_service:
        # Generate auth token for User Service API calls
        auth_token = None
        try:
            from ..components.user_service import user_service
            client = user_service._get_client()
            token_response = client.post(f"{user_service.base_url}/auth/dev-token?user_id=session_service&email=session@service.com")
            if token_response.status_code == 200:
                token_data = token_response.json()
                auth_token = token_data.get("token")
        except Exception as e:
            api_logger.warning(f"Failed to get auth token for SessionService: {e}")
        
        session_service = SessionService(auth_token=auth_token)
        api_logger.info("= Session API: SessionService initialized")
    
    return session_service

@router.get("/health")
async def session_health():
    """Session service health check"""
    try:
        manager = await get_session_service()
        
        # Check User Service API connection
        api_connected = False
        try:
            from ..components.user_service import user_service
            health_result = user_service.health_check()
            api_connected = health_result.get("status") == "healthy"
        except Exception:
            api_connected = False
        
        # Get basic stats
        active_sessions = len(manager.get_active_sessions())
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Session service is healthy",
                "status": {
                    "service": "operational",
                    "user_service_connected": api_connected,
                    "active_sessions": active_sessions,
                    "timestamp": datetime.now().isoformat()
                }
            }
        )
        
    except Exception as e:
        api_logger.error(f"L Session health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": "Session service is unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/search")
async def search_sessions(
    query: str = Query(..., description="Search query"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Search across sessions"""
    return await list_sessions(
        user_id=user_id,
        search=query,
        limit=limit,
        offset=offset
    )

@router.post("", response_model=SessionDetailResponse)
async def create_session(
    request: Request,
    user_id: str = Query("anonymous", description="User ID"),
    title: Optional[str] = Query(None, description="Session title"),
    metadata: Optional[str] = Query("{}", description="Session metadata as JSON string")
):
    """Create a new session"""
    try:
        manager = await get_session_service()
        
        # Extract user's Auth token from request headers
        auth_header = request.headers.get("Authorization")
        user_token = None
        if auth_header and auth_header.startswith("Bearer "):
            user_token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Set the user's token for this operation
        if user_token:
            manager.set_auth_token(user_token)
        
        # Parse metadata
        session_metadata = {}
        if metadata:
            try:
                session_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        # Create session
        session_id = await manager.create_session(user_id=user_id, title=title)
        session_data = await manager.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        # Update title and metadata if provided
        if title:
            session_data["title"] = title
        if session_metadata:
            if "metadata" not in session_data:
                session_data["metadata"] = {}
            session_data["metadata"].update(session_metadata)
        
        # Convert to response format
        session_response = SessionData(
            id=session_data["id"],
            user_id=session_data["user_id"],
            title=session_data.get("title", f"Session {session_data['id'][:8]}"),
            created_at=session_data["created_at"],
            last_activity=session_data["last_activity"],
            message_count=session_data["message_count"],
            summary=session_data["summary"],
            metadata=session_data["metadata"]
        )
        
        api_logger.info(f" Created session: {session_id} for user: {user_id}")
        
        return SessionDetailResponse(
            success=True,
            message="Session created successfully",
            session=session_response
        )
        
    except Exception as e:
        api_logger.error(f"L Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str = Path(..., description="Session ID"),
    include_history: bool = Query(False, description="Include conversation history"),
    include_stats: bool = Query(False, description="Include session statistics")
):
    """Get session details"""
    try:
        manager = await get_session_service()
        
        if include_history or include_stats:
            session_data = await manager.get_session_with_history(session_id)
        else:
            session_data = await manager.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Convert to response format
        session_response = SessionData(
            id=session_data["id"],
            user_id=session_data["user_id"],
            title=session_data.get("title", f"Session {session_data['id'][:8]}"),
            created_at=session_data["created_at"],
            last_activity=session_data["last_activity"],
            message_count=session_data["message_count"],
            summary=session_data["summary"],
            metadata=session_data.get("metadata", {})
        )
        
        return SessionDetailResponse(
            success=True,
            message="Session retrieved successfully",
            session=session_response,
            conversation_history=session_data.get("conversation_history") if include_history else None,
            stats=session_data.get("stats") if include_stats else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"L Error getting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@router.put("/{session_id}", response_model=SessionDetailResponse)
async def update_session(
    session_id: str = Path(..., description="Session ID"),
    title: Optional[str] = Query(None, description="New session title"),
    tags: Optional[str] = Query(None, description="Session tags as JSON array"),
    metadata: Optional[str] = Query(None, description="Session metadata as JSON string")
):
    """Update session metadata"""
    try:
        manager = await get_session_service()
        session_data = await manager.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update fields
        if title is not None:
            session_data["title"] = title
        
        if tags is not None:
            try:
                session_data["tags"] = json.loads(tags)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid tags JSON")
        
        if metadata is not None:
            try:
                new_metadata = json.loads(metadata)
                session_data["metadata"].update(new_metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        # Update last activity
        session_data["last_activity"] = datetime.now()
        
        # Convert to response format
        session_response = SessionData(
            id=session_data["id"],
            user_id=session_data["user_id"],
            title=session_data.get("title", f"Session {session_data['id'][:8]}"),
            created_at=session_data["created_at"],
            last_activity=session_data["last_activity"],
            message_count=session_data["message_count"],
            summary=session_data["summary"],
            tags=session_data.get("tags", []),
            metadata=session_data.get("metadata", {})
        )
        
        api_logger.info(f" Updated session: {session_id}")
        
        return SessionDetailResponse(
            success=True,
            message="Session updated successfully",
            session=session_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"L Error updating session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

@router.delete("/{session_id}")
async def delete_session(
    session_id: str = Path(..., description="Session ID")
):
    """Delete a session"""
    try:
        manager = await get_session_service()
        session_data = await manager.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await manager.clear_session(session_id)
        
        api_logger.info(f"=� Deleted session: {session_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Session deleted successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"L Error deleting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@router.get("", response_model=SessionListResponse)
async def list_sessions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query("active", description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Number of sessions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    search: Optional[str] = Query(None, description="Search in session titles and summaries")
):
    """List sessions with optional filtering"""
    try:
        manager = await get_session_service()
        
        if user_id:
            user_sessions = await manager.get_user_sessions(user_id)
        else:
            # Get all active sessions if no user specified
            user_sessions = []
            for session_id in manager.get_active_sessions():
                session_data = await manager.get_session(session_id)
                if session_data:
                    user_sessions.append(session_data)
        
        # Apply filters
        filtered_sessions = []
        for session_data in user_sessions:
            # Status filter
            if status and session_data.get("status", "active") != status:
                continue
            
            # Search filter
            if search:
                search_text = search.lower()
                title = session_data.get("title", "").lower()
                summary = session_data.get("summary", "").lower()
                if search_text not in title and search_text not in summary:
                    continue
            
            filtered_sessions.append(session_data)
        
        # Sort by last activity (newest first)
        filtered_sessions.sort(
            key=lambda x: x.get("last_activity", datetime.min),
            reverse=True
        )
        
        # Apply pagination
        total_count = len(filtered_sessions)
        paginated_sessions = filtered_sessions[offset:offset + limit]
        
        # Convert to response format
        session_responses = []
        for session_data in paginated_sessions:
            # Handle User Service API format vs local cache format
            if "session_id" in session_data:
                # User Service API format
                session_id = session_data["session_id"]
                title = session_data.get("conversation_data", {}).get("topic", f"Session {session_id[:8]}")
                
                # Parse datetime strings from API
                def parse_datetime(dt_str):
                    if isinstance(dt_str, str):
                        try:
                            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                        except:
                            try:
                                return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%f%z")
                            except:
                                pass
                    return datetime.now()
                
                created_at = parse_datetime(session_data.get("created_at"))
                last_activity = parse_datetime(session_data.get("last_activity"))
            else:
                # Local cache format
                session_id = session_data["id"]
                title = session_data.get("title", f"Session {session_id[:8]}")
                created_at = session_data["created_at"]
                last_activity = session_data["last_activity"]
            
            session_responses.append(SessionData(
                id=session_id,
                user_id=session_data["user_id"],
                title=title,
                created_at=created_at,
                last_activity=last_activity,
                message_count=session_data.get("message_count", 0),
                summary=session_data.get("summary", session_data.get("session_summary", "")),
                tags=session_data.get("tags", []),
                metadata=session_data.get("metadata", {})
            ))
        
        pagination_info = {
            "total": total_count,
            "page": (offset // limit) + 1,
            "per_page": limit,
            "has_more": offset + limit < total_count
        }
        
        return SessionListResponse(
            success=True,
            message=f"Retrieved {len(session_responses)} sessions",
            sessions=session_responses,
            pagination=pagination_info
        )
        
    except Exception as e:
        api_logger.error(f"L Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@router.get("/user/{user_id}", response_model=SessionListResponse)
async def get_user_sessions(
    user_id: str = Path(..., description="User ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of sessions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get all sessions for a specific user"""
    return await list_sessions(user_id=user_id, limit=limit, offset=offset)

@router.get("/active", response_model=SessionListResponse)
async def get_active_sessions(
    limit: int = Query(20, ge=1, le=100, description="Number of sessions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get currently active sessions"""
    return await list_sessions(status="active", limit=limit, offset=offset)

@router.get("/{session_id}/messages", response_model=ChatHistoryResponse)
async def get_session_messages(
    request: Request,
    session_id: str = Path(..., description="Session ID"),
    user_id: Optional[str] = Query(None, description="User ID (required for API lookup)"),
    limit: int = Query(20, ge=1, le=100, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    role: Optional[str] = Query(None, description="Filter by role (user/assistant/system)")
):
    """Get chat history for a session"""
    try:
        manager = await get_session_service()
        
        # Extract user's Auth token from request headers
        auth_header = request.headers.get("Authorization")
        user_token = None
        if auth_header and auth_header.startswith("Bearer "):
            user_token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Set the user's token for this operation
        if user_token:
            manager.set_auth_token(user_token)
        
        # Try to get session with user_id if provided
        if user_id:
            session_data = await manager.get_session(session_id, user_id=user_id)
        else:
            session_data = await manager.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get history from User Service API via SessionService
        try:
            # Get conversation history with pagination via User Service API
            from ..components.user_service import user_service
            
            messages_result = user_service.get_session_messages(
                session_id=session_id,
                limit=limit,
                offset=offset,
                role=role,
                auth_token=manager.auth_token
            )
            
            if messages_result.get("success"):
                api_messages = messages_result.get("data", [])
                
                # Convert to message format
                messages = []
                for msg in api_messages:
                    messages.append(MessageData(
                        id=msg.get("id", f"msg_{len(messages)}"),
                        session_id=session_id,
                        role=msg.get("role", "user"),
                        content=msg.get("content", {}),
                        timestamp=msg.get("timestamp", datetime.now()),
                        token_count=msg.get("token_count"),
                        metadata=msg.get("metadata", {})
                    ))
                
                # Get total count from pagination info
                pagination = messages_result.get("pagination", {})
                total_count = pagination.get("total", len(messages))
                
                pagination_info = {
                    "total": total_count,
                    "page": (offset // limit) + 1,
                    "per_page": limit,
                    "has_more": offset + limit < total_count
                }
                
            else:
                # API call failed, return empty result
                messages = []
                total_count = 0
                pagination_info = {
                    "total": 0,
                    "page": 1,
                    "per_page": limit,
                    "has_more": False
                }
                
            return ChatHistoryResponse(
                success=True,
                message=f"Retrieved {len(messages)} messages",
                messages=messages,
                pagination=pagination_info
            )
                
        except Exception as e:
            api_logger.error(f"⚠️ Error getting session history: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to get session history")
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"L Error getting messages for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@router.get("/{session_id}/context")
async def get_session_context(
    session_id: str = Path(..., description="Session ID")
):
    """Get session context"""
    try:
        manager = await get_session_service()
        session_data = await manager.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        context = session_data.get("context", {})
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Session context retrieved successfully",
                "context": context
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"L Error getting context for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session context: {str(e)}")

@router.put("/{session_id}/context")
async def update_session_context(
    session_id: str = Path(..., description="Session ID"),
    context: Dict[str, Any] = Body(...)
):
    """Update session context"""
    try:
        manager = await get_session_service()
        session_data = await manager.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update context
        for key, value in context.items():
            manager.set_session_context(session_id, key, value)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Session context updated successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"L Error updating context for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update session context: {str(e)}")

@router.delete("/{session_id}/context")
async def clear_session_context(
    session_id: str = Path(..., description="Session ID")
):
    """Clear session context"""
    try:
        manager = await get_session_service()
        session_data = await manager.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Clear context
        session_data["context"] = {}
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Session context cleared successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"L Error clearing context for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear session context: {str(e)}")

@router.get("/{session_id}/stats", response_model=SessionStatsResponse)
async def get_session_stats(
    session_id: str = Path(..., description="Session ID")
):
    """Get session statistics"""
    try:
        manager = await get_session_service()
        session_data = await manager.get_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get stats from database if available
        stats = {}
        if manager.db_service and manager.db_service.is_connected():
            try:
                stats = await manager.get_session_with_history(session_id)
            except Exception as e:
                api_logger.warning(f"� Could not get detailed stats: {str(e)}")
        
        # Basic stats from session data
        basic_stats = {
            "message_count": session_data["message_count"],
            "created_at": session_data["created_at"].isoformat(),
            "last_activity": session_data["last_activity"].isoformat(),
            "duration_minutes": (session_data["last_activity"] - session_data["created_at"]).total_seconds() / 60,
            "status": session_data.get("status", "active")
        }
        
        # Merge with detailed stats
        stats.update(basic_stats)
        
        return SessionStatsResponse(
            success=True,
            message="Session statistics retrieved successfully",
            stats=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"L Error getting stats for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session stats: {str(e)}")

@router.get("/{session_id}/export")
async def export_session(
    session_id: str = Path(..., description="Session ID"),
    format: str = Query("json", description="Export format (json, csv, txt)")
):
    """Export session data"""
    try:
        manager = await get_session_service()
        session_data = await manager.get_session_with_history(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if format == "json":
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Session exported successfully",
                    "data": {
                        "session": {
                            "id": session_data["id"],
                            "user_id": session_data["user_id"],
                            "created_at": session_data["created_at"].isoformat(),
                            "last_activity": session_data["last_activity"].isoformat(),
                            "message_count": session_data["message_count"],
                            "summary": session_data["summary"],
                            "metadata": session_data.get("metadata", {})
                        },
                        "conversation_history": session_data.get("conversation_history", []),
                        "stats": session_data.get("stats", {})
                    }
                }
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"L Error exporting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export session: {str(e)}")

