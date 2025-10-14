"""
Modular components for isA_Agent
Includes production-grade MCP service, model service and session management
"""

from .session_service import SessionService
from .mcp_service import MCPService
from .model_service import ModelService, get_model_service
from .billing_service import billing_service, create_billing_handler, track_model_call, track_tool_call
# Microservices-based user_service (replaces monolithic User Service at port 8100)
from .user_service import user_service

__all__ = [
    "SessionService",
    "MCPService",
    "ModelService",
    "get_model_service",
    "billing_service",
    "create_billing_handler",
    "track_model_call",
    "track_tool_call",
    "user_service"  # Microservices-based implementation
]