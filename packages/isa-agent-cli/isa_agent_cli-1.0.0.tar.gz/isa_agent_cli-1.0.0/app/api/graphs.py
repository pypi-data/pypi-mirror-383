#!/usr/bin/env python3
"""
Graph Management API

Endpoints for managing and selecting different graph implementations.
Integrates with authorization service for permission-based access control.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from ..graphs.graph_registry_with_auth import get_graph_registry, GraphType
from .auth import require_chat_permission, require_admin_permission
from ..utils.logger import api_logger

router = APIRouter(prefix="/api/v1/graphs", tags=["graphs"])


# Request/Response Models
class GraphSelectionRequest(BaseModel):
    """Request to select a graph for a user"""
    user_id: str = Field(..., description="User ID")
    graph_type: str = Field(..., description="Graph type to select")
    

class GraphTaskRequest(BaseModel):
    """Request for automatic graph selection based on task"""
    user_id: str = Field(..., description="User ID")
    task_description: str = Field(..., description="Task description")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class GraphAccessRequest(BaseModel):
    """Request to grant graph access"""
    user_id: str = Field(..., description="User to grant access to")
    graph_type: str = Field(..., description="Graph type")
    access_level: str = Field(default="read_only", description="Access level")
    expires_in_days: Optional[int] = Field(None, description="Expiration in days")
    reason: Optional[str] = Field(None, description="Reason for grant")


class GraphInfo(BaseModel):
    """Graph information response"""
    type: str
    name: str
    description: str
    access_level: Optional[str]
    features: List[str]
    subscription_tier: Optional[str]
    is_active: bool


class GraphListResponse(BaseModel):
    """Response with list of available graphs"""
    user_id: str
    available_graphs: List[GraphInfo]
    active_graph: Optional[str]


# API Endpoints

@router.get("/available/{user_id}", response_model=GraphListResponse)
async def get_available_graphs(
    user_id: str,
    api_key_info: dict = Depends(require_chat_permission)
):
    """Get list of graphs available to a specific user"""
    try:
        registry = get_graph_registry()
        available = await registry.get_available_graphs(user_id)
        
        # Get active graph
        active_graphs = registry._active_graphs
        active = active_graphs.get(user_id)
        
        api_logger.info(f"Retrieved {len(available)} available graphs for user {user_id}")
        
        return GraphListResponse(
            user_id=user_id,
            available_graphs=[GraphInfo(**g) for g in available],
            active_graph=active
        )
        
    except Exception as e:
        api_logger.error(f"Failed to get available graphs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select")
async def select_graph(
    request: GraphSelectionRequest,
    api_key_info: dict = Depends(require_chat_permission)
):
    """Select and activate a specific graph for a user"""
    try:
        registry = get_graph_registry()
        
        # Try to set active graph
        result = await registry.set_active_graph(request.user_id, request.graph_type)
        
        if result is None:
            api_logger.warning(f"User {request.user_id} denied access to {request.graph_type}")
            raise HTTPException(
                status_code=403,
                detail=f"Access denied to graph type: {request.graph_type}"
            )
        
        api_logger.info(f"User {request.user_id} activated graph: {result}")
        
        return {
            "success": True,
            "user_id": request.user_id,
            "active_graph": result,
            "message": f"Graph {result} activated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Failed to select graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-select")
async def auto_select_graph(
    request: GraphTaskRequest,
    api_key_info: dict = Depends(require_chat_permission)
):
    """Automatically select the best graph for a task"""
    try:
        registry = get_graph_registry()
        
        # Auto-select based on task
        selected = await registry.select_graph_for_task(
            request.user_id,
            request.task_description,
            request.context
        )
        
        # Set as active
        result = await registry.set_active_graph(request.user_id, selected)
        
        if result is None:
            # Fallback occurred
            selected = GraphType.DEFAULT
            result = await registry.set_active_graph(request.user_id, selected)
        
        api_logger.info(f"Auto-selected {selected} for user {request.user_id}")
        
        return {
            "success": True,
            "user_id": request.user_id,
            "selected_graph": selected,
            "task": request.task_description,
            "message": f"Graph {selected} selected for task"
        }
        
    except Exception as e:
        api_logger.error(f"Failed to auto-select graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active/{user_id}")
async def get_active_graph(
    user_id: str,
    api_key_info: dict = Depends(require_chat_permission)
):
    """Get the currently active graph for a user"""
    try:
        registry = get_graph_registry()
        active = registry._active_graphs.get(user_id, GraphType.DEFAULT)
        
        # Get graph info
        info = await registry.get_graph_info(active)
        
        api_logger.info(f"Retrieved active graph for user {user_id}: {active}")
        
        return {
            "user_id": user_id,
            "active_graph": active,
            "graph_info": info
        }
        
    except Exception as e:
        api_logger.error(f"Failed to get active graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grant-access")
async def grant_graph_access(
    request: GraphAccessRequest,
    api_key_info: dict = Depends(require_admin_permission)
):
    """Grant a user access to a specific graph (admin only)"""
    try:
        registry = get_graph_registry()
        admin_id = api_key_info.get("user_id", "admin")
        
        # Grant access
        success = await registry.grant_graph_access(
            admin_id=admin_id,
            user_id=request.user_id,
            graph_type=request.graph_type,
            access_level=request.access_level,
            expires_in_days=request.expires_in_days,
            reason=request.reason
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to grant graph access"
            )
        
        api_logger.info(f"Admin {admin_id} granted {request.user_id} access to {request.graph_type}")
        
        return {
            "success": True,
            "user_id": request.user_id,
            "graph_type": request.graph_type,
            "access_level": request.access_level,
            "granted_by": admin_id,
            "message": "Graph access granted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Failed to grant graph access: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def list_graph_types():
    """List all available graph types (public endpoint)"""
    try:
        return {
            "graph_types": [
                {
                    "type": GraphType.DEFAULT,
                    "name": "Default Smart Agent",
                    "description": "Standard agent with full features",
                    "subscription_required": "free"
                },
                {
                    "type": GraphType.RESEARCH,
                    "name": "Research Graph",
                    "description": "Deep research with enhanced search",
                    "subscription_required": "pro"
                },
                {
                    "type": GraphType.CODING,
                    "name": "Coding Graph",
                    "description": "Code generation and debugging",
                    "subscription_required": "pro"
                },
                {
                    "type": GraphType.CONVERSATION,
                    "name": "Conversation Graph",
                    "description": "Simple chat without tools",
                    "subscription_required": "free"
                }
            ]
        }
        
    except Exception as e:
        api_logger.error(f"Failed to list graph types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_graph_statistics(
    api_key_info: dict = Depends(require_admin_permission)
):
    """Get graph registry statistics (admin only)"""
    try:
        registry = get_graph_registry()
        stats = registry.get_statistics()
        
        api_logger.info("Retrieved graph registry statistics")
        
        return {
            "statistics": stats,
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
    except Exception as e:
        api_logger.error(f"Failed to get graph statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_graphs_info():
    """Get general information about the graph system (public)"""
    return {
        "service": "Graph Management System",
        "version": "1.0",
        "description": "Multi-graph system with permission-based access control",
        "features": [
            "Multiple specialized graphs",
            "Permission-based access control",
            "Automatic graph selection",
            "User-specific graph instances",
            "Integration with authorization service"
        ],
        "available_graphs": 4,
        "authentication_required": True,
        "admin_endpoints": ["/grant-access", "/stats"],
        "subscription_tiers": {
            "free": ["default", "conversation"],
            "pro": ["default", "conversation", "research", "coding"],
            "enterprise": ["all"]
        }
    }