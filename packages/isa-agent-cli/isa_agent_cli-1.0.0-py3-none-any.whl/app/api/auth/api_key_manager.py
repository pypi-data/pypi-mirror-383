"""
API Key Authentication System
Secure API access with rate limiting and key management
"""
import hashlib
import secrets
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict, deque

from fastapi import HTTPException, Security, Depends, Request
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery, APIKeyCookie
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_429_TOO_MANY_REQUESTS

from app.config import settings
from app.utils.logger import api_logger


class APIKeyManager:
    """Manage API keys with rate limiting and validation"""
    
    def __init__(self):
        # API Key storage (in production, use database)
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        
        # Rate limiting storage
        self.rate_limits: Dict[str, deque] = defaultdict(deque)
        self.blocked_keys: Dict[str, float] = {}  # key -> unblock_time
        
        # Default rate limits
        self.default_requests_per_minute = 60
        self.default_requests_per_hour = 1000
        self.default_block_duration = 300  # 5 minutes
        
        # Load API keys from environment
        self._load_default_keys()
    
    def _load_default_keys(self):
        """Load API keys from environment variables"""
        # Master admin key
        admin_key = settings.api_master_key if hasattr(settings, 'api_master_key') else None
        if admin_key:
            self.api_keys[admin_key] = {
                "name": "master_admin",
                "permissions": ["*"],  # All permissions
                "rate_limit_rpm": 300,  # Higher limits for admin
                "rate_limit_rph": 5000,
                "created_at": datetime.now(),
                "is_active": True
            }
        
        # Development key
        dev_key = "dev_key_" + secrets.token_urlsafe(32)
        if settings.environment == "dev":
            self.api_keys[dev_key] = {
                "name": "development_key",
                "permissions": ["chat", "health", "stats"],
                "rate_limit_rpm": 120,
                "rate_limit_rph": 2000,
                "created_at": datetime.now(),
                "is_active": True
            }
            api_logger.info(f"🔑 Development API Key: {dev_key}")
    
    def generate_api_key(self, name: str, permissions: list = None, rate_limits: dict = None) -> str:
        """Generate a new API key"""
        api_key = "isa_" + secrets.token_urlsafe(32)
        
        self.api_keys[api_key] = {
            "name": name,
            "permissions": permissions or ["chat"],
            "rate_limit_rpm": rate_limits.get("rpm", self.default_requests_per_minute) if rate_limits else self.default_requests_per_minute,
            "rate_limit_rph": rate_limits.get("rph", self.default_requests_per_hour) if rate_limits else self.default_requests_per_hour,
            "created_at": datetime.now(),
            "is_active": True,
            "usage_count": 0,
            "last_used": None
        }
        
        api_logger.info(f"🔑 Generated new API key for '{name}': {api_key[:12]}...")
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return key info"""
        if not api_key:
            return None
            
        key_info = self.api_keys.get(api_key)
        if not key_info or not key_info.get("is_active", False):
            return None
        
        # Update usage stats
        key_info["usage_count"] = key_info.get("usage_count", 0) + 1
        key_info["last_used"] = datetime.now()
        
        return key_info
    
    def check_rate_limit(self, api_key: str, key_info: Dict[str, Any]) -> bool:
        """Check if request is within rate limits"""
        now = time.time()
        
        # Check if key is currently blocked
        if api_key in self.blocked_keys:
            if now < self.blocked_keys[api_key]:
                return False  # Still blocked
            else:
                del self.blocked_keys[api_key]  # Unblock
        
        # Get rate limits for this key
        rpm_limit = key_info.get("rate_limit_rpm", self.default_requests_per_minute)
        rph_limit = key_info.get("rate_limit_rph", self.default_requests_per_hour)
        
        # Initialize rate limiting queues
        if api_key not in self.rate_limits:
            self.rate_limits[api_key] = deque()
        
        requests = self.rate_limits[api_key]
        
        # Remove old requests (older than 1 hour)
        while requests and requests[0] < now - 3600:
            requests.popleft()
        
        # Check hourly limit
        if len(requests) >= rph_limit:
            self._block_key(api_key, "Hourly rate limit exceeded")
            return False
        
        # Check minute limit
        minute_requests = sum(1 for req_time in requests if req_time > now - 60)
        if minute_requests >= rpm_limit:
            self._block_key(api_key, "Per-minute rate limit exceeded")
            return False
        
        # Add current request
        requests.append(now)
        
        return True
    
    def _block_key(self, api_key: str, reason: str):
        """Block an API key temporarily"""
        block_until = time.time() + self.default_block_duration
        self.blocked_keys[api_key] = block_until
        
        key_info = self.api_keys.get(api_key, {})
        key_name = key_info.get("name", api_key[:12])
        
        api_logger.warning(f"🚫 Blocked API key '{key_name}' for {self.default_block_duration}s: {reason}")
    
    def check_permission(self, api_key: str, required_permission: str) -> bool:
        """Check if API key has required permission"""
        key_info = self.api_keys.get(api_key)
        if not key_info:
            return False
        
        permissions = key_info.get("permissions", [])
        return "*" in permissions or required_permission in permissions
    
    def get_key_stats(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Get usage statistics for an API key"""
        key_info = self.api_keys.get(api_key)
        if not key_info:
            return None
        
        now = time.time()
        requests = self.rate_limits.get(api_key, deque())
        
        # Count recent requests
        last_minute = sum(1 for req_time in requests if req_time > now - 60)
        last_hour = len(requests)
        
        return {
            "name": key_info.get("name"),
            "total_usage": key_info.get("usage_count", 0),
            "last_used": key_info.get("last_used"),
            "requests_last_minute": last_minute,
            "requests_last_hour": last_hour,
            "rate_limits": {
                "rpm": key_info.get("rate_limit_rpm"),
                "rph": key_info.get("rate_limit_rph")
            },
            "is_blocked": api_key in self.blocked_keys
        }


# Global API key manager instance
api_key_manager = APIKeyManager()

# FastAPI Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)
api_key_cookie = APIKeyCookie(name="api_key", auto_error=False)


async def get_api_key(
    request: Request,
    api_key_header: str = Security(api_key_header),
    api_key_query: str = Security(api_key_query),
    api_key_cookie: str = Security(api_key_cookie),
) -> str:
    """Extract API key from request - DISABLED FOR NOW"""
    # TEMPORARY: No authentication required
    return "no_auth_bypass"


async def validate_api_key(
    request: Request,
    api_key: str = Depends(get_api_key),
    required_permission: str = "chat"
) -> Dict[str, Any]:
    """Validate API key and check permissions - DISABLED FOR NOW"""
    
    # TEMPORARY: No authentication required, return default permissions
    return {
        "name": "no_auth_bypass",
        "permissions": ["*"],
        "rate_limit_rpm": 10000,
        "rate_limit_rph": 100000
    }
    
    # Check permissions
    if not api_key_manager.check_permission(api_key, required_permission):
        api_logger.warning(f"🚫 Insufficient permissions for key: {key_info.get('name', api_key[:12])}")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"API key does not have permission: {required_permission}"
        )
    
    return key_info


# Convenience functions for different permission levels
async def require_chat_permission(request: Request, api_key: str = Depends(get_api_key)):
    """Require chat permission"""
    return await validate_api_key(request, api_key, "chat")

async def require_admin_permission(request: Request, api_key: str = Depends(get_api_key)):
    """Require admin permission"""
    return await validate_api_key(request, api_key, "admin")

async def require_read_permission(request: Request, api_key: str = Depends(get_api_key)):
    """Require read-only permission"""
    return await validate_api_key(request, api_key, "read")