"""
Authentication and API Key Management API
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from .api_key_manager import api_key_manager, require_admin_permission, require_read_permission
from ...utils.logger import api_logger


class APIKeyCreateRequest(BaseModel):
    name: str
    permissions: Optional[List[str]] = ["chat"]
    rate_limit_rpm: Optional[int] = 60
    rate_limit_rph: Optional[int] = 1000


class APIKeyResponse(BaseModel):
    api_key: str
    name: str
    permissions: List[str]
    rate_limits: Dict[str, int]
    created_at: datetime


class APIKeyStatsResponse(BaseModel):
    name: str
    total_usage: int
    last_used: Optional[datetime]
    requests_last_minute: int
    requests_last_hour: int
    rate_limits: Dict[str, int]
    is_blocked: bool


router = APIRouter(prefix="/api/v1/agents/auth", tags=["authentication"])


@router.post("/keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyCreateRequest,
    api_key_info: dict = Depends(require_admin_permission)
):
    """Create a new API key (Admin only)"""
    try:
        api_key = api_key_manager.generate_api_key(
            name=request.name,
            permissions=request.permissions,
            rate_limits={
                "rpm": request.rate_limit_rpm,
                "rph": request.rate_limit_rph
            }
        )
        
        key_info = api_key_manager.api_keys[api_key]
        
        api_logger.info(f"🔑 API key created by admin: {request.name}")
        
        return APIKeyResponse(
            api_key=api_key,
            name=key_info["name"],
            permissions=key_info["permissions"],
            rate_limits={
                "rpm": key_info["rate_limit_rpm"],
                "rph": key_info["rate_limit_rph"]
            },
            created_at=key_info["created_at"]
        )
        
    except Exception as e:
        api_logger.error(f"❌ Failed to create API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys")
async def list_api_keys(api_key_info: dict = Depends(require_admin_permission)):
    """List all API keys (Admin only)"""
    try:
        keys_info = []
        for key, info in api_key_manager.api_keys.items():
            keys_info.append({
                "key_preview": f"{key[:12]}...",
                "name": info["name"],
                "permissions": info["permissions"],
                "created_at": info["created_at"],
                "is_active": info["is_active"],
                "usage_count": info.get("usage_count", 0),
                "last_used": info.get("last_used")
            })
        
        return {"keys": keys_info, "total": len(keys_info)}
        
    except Exception as e:
        api_logger.error(f"❌ Failed to list API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys/{key_id}/stats", response_model=APIKeyStatsResponse)
async def get_api_key_stats(
    key_id: str,
    api_key_info: dict = Depends(require_admin_permission)
):
    """Get API key usage statistics (Admin only)"""
    try:
        # Find key by ID or name
        target_key = None
        for key, info in api_key_manager.api_keys.items():
            if key.startswith(key_id) or info["name"] == key_id:
                target_key = key
                break
        
        if not target_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        stats = api_key_manager.get_key_stats(target_key)
        if not stats:
            raise HTTPException(status_code=404, detail="API key not found")
        
        return APIKeyStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"❌ Failed to get API key stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    api_key_info: dict = Depends(require_admin_permission)
):
    """Revoke an API key (Admin only)"""
    try:
        # Find key by ID or name
        target_key = None
        for key, info in api_key_manager.api_keys.items():
            if key.startswith(key_id) or info["name"] == key_id:
                target_key = key
                break
        
        if not target_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        key_info = api_key_manager.api_keys[target_key]
        key_info["is_active"] = False
        
        api_logger.info(f"🔑 API key revoked: {key_info['name']}")
        
        return {"message": f"API key '{key_info['name']}' has been revoked"}
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"❌ Failed to revoke API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage")
async def get_my_usage(
    request: Request,
    api_key_info: dict = Depends(require_read_permission)
):
    """Get current API key usage statistics"""
    try:
        # Get the API key from the request
        from .api_key_manager import get_api_key
        api_key = await get_api_key(request)
        
        if api_key == "dev_bypass":
            return {
                "name": "development_bypass",
                "usage": "unlimited",
                "rate_limits": {"rpm": 1000, "rph": 10000}
            }
        
        stats = api_key_manager.get_key_stats(api_key)
        if not stats:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Don't expose sensitive information
        return {
            "name": stats["name"],
            "requests_last_minute": stats["requests_last_minute"],
            "requests_last_hour": stats["requests_last_hour"],
            "rate_limits": stats["rate_limits"],
            "is_blocked": stats["is_blocked"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"❌ Failed to get usage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/info")
async def get_auth_info():
    """Get authentication information (public endpoint)"""
    return {
        "authentication_required": True,
        "methods": [
            "X-API-Key header",
            "api_key query parameter", 
            "api_key cookie"
        ],
        "rate_limits": {
            "default_rpm": 60,
            "default_rph": 1000
        },
        "permissions": [
            "chat",
            "read", 
            "admin"
        ],
        "development_mode": api_key_manager.api_keys.get("dev_bypass") is not None
    }