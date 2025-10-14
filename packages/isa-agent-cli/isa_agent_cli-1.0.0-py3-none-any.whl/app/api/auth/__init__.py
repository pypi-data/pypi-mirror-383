"""
Authentication module for isA Agent API
Centralized auth functionality under api/auth/
"""

from .api_key_manager import (
    api_key_manager,
    get_api_key,
    validate_api_key,
    require_chat_permission,
    require_admin_permission,
    require_read_permission
)

from .routes import router as auth_router

__all__ = [
    "api_key_manager",
    "get_api_key", 
    "validate_api_key",
    "require_chat_permission",
    "require_admin_permission",
    "require_read_permission",
    "auth_router"
]