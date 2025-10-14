"""
API模块 - 模块化的API端点
"""
try:
    from .main import app
    MAIN_APP_AVAILABLE = True
except ImportError:
    MAIN_APP_AVAILABLE = False

# Import individual routers
from .chat import router as chat_router
from .execution import router as execution_router

# Export all routers
__all__ = [
    'chat_router',
    'execution_router',
]

# Export main app if available
if MAIN_APP_AVAILABLE:
    __all__.append('app')