#!/usr/bin/env python3
"""
LangSmith Tracing Service

Centralized service for managing LangSmith tracing configuration
and integration with the existing ISA Agent system.
"""

import os
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


class TracingService:
    """
    Centralized tracing service for LangSmith integration
    
    Provides non-invasive tracing capabilities that can be enabled/disabled
    without affecting core functionality.
    """
    
    def __init__(self):
        self._initialized = False
        self._tracing_enabled = False
        self._traceable_decorator = None
        
    def initialize(
        self,
        api_key: Optional[str] = None,
        project: str = "isa_agent",
        endpoint: str = "https://api.smith.langchain.com",
        enabled: bool = True
    ) -> bool:
        """
        Initialize LangSmith tracing
        
        Args:
            api_key: LangSmith API key
            project: Project name for traces
            endpoint: LangSmith API endpoint
            enabled: Whether to enable tracing
            
        Returns:
            True if initialization successful
        """
        try:
            if enabled:
                # Set environment variables
                os.environ["LANGSMITH_TRACING"] = "true"
                os.environ["LANGSMITH_ENDPOINT"] = endpoint
                os.environ["LANGSMITH_PROJECT"] = project
                
                if api_key:
                    os.environ["LANGSMITH_API_KEY"] = api_key
                elif not os.getenv("LANGSMITH_API_KEY"):
                    logger.warning("No LANGSMITH_API_KEY found - tracing may not work")
                
                # Try to import and configure langsmith
                try:
                    from langsmith import traceable
                    self._traceable_decorator = traceable
                    self._tracing_enabled = True
                    logger.info(f"LangSmith tracing enabled for project: {project}")
                    logger.info(f"LangSmith endpoint: {endpoint}")
                except ImportError:
                    logger.warning("langsmith package not installed - tracing disabled")
                    self._tracing_enabled = False
                    self._traceable_decorator = self._noop_decorator
            else:
                os.environ["LANGSMITH_TRACING"] = "false"
                self._tracing_enabled = False
                self._traceable_decorator = self._noop_decorator
                logger.info("LangSmith tracing disabled")
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")
            self._tracing_enabled = False
            self._traceable_decorator = self._noop_decorator
            self._initialized = True
            return False
    
    def _noop_decorator(self, func: Callable) -> Callable:
        """No-op decorator when tracing is disabled"""
        return func
    
    def get_traceable_decorator(self) -> Callable:
        """
        Get traceable decorator
        
        Returns:
            traceable decorator if available, no-op decorator otherwise
        """
        if not self._initialized:
            # Auto-initialize with defaults if not initialized
            self.initialize()
        
        return self._traceable_decorator or self._noop_decorator
    
    def is_enabled(self) -> bool:
        """Check if tracing is enabled"""
        return self._tracing_enabled and self._initialized
    
    def get_config(self) -> Dict[str, Optional[str]]:
        """
        Get current tracing configuration
        
        Returns:
            Dictionary with current settings
        """
        return {
            "enabled": self._tracing_enabled,
            "tracing": os.getenv("LANGSMITH_TRACING"),
            "project": os.getenv("LANGSMITH_PROJECT"),
            "endpoint": os.getenv("LANGSMITH_ENDPOINT"),
            "has_api_key": bool(os.getenv("LANGSMITH_API_KEY"))
        }
    
    def configure_from_env(self) -> bool:
        """
        Configure tracing from environment variables
        
        Returns:
            True if configuration successful
        """
        enabled = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        api_key = os.getenv("LANGSMITH_API_KEY")
        project = os.getenv("LANGSMITH_PROJECT", "isa_agent")
        endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        
        return self.initialize(
            api_key=api_key,
            project=project,
            endpoint=endpoint,
            enabled=enabled
        )


# Global singleton instance
_tracing_service: Optional[TracingService] = None


def get_tracing_service() -> TracingService:
    """Get global tracing service singleton"""
    global _tracing_service
    if _tracing_service is None:
        _tracing_service = TracingService()
    return _tracing_service


def traceable_if_enabled(func: Callable) -> Callable:
    """
    Decorator that applies traceable only if tracing is enabled
    
    Usage:
        @traceable_if_enabled
        def my_function():
            pass
    """
    service = get_tracing_service()
    decorator = service.get_traceable_decorator()
    return decorator(func)


def setup_tracing(
    api_key: str = "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",
    project: str = "isa_agent",
    enabled: bool = True
) -> bool:
    """
    Convenience function to setup tracing with provided configuration
    
    Args:
        api_key: LangSmith API key
        project: Project name
        enabled: Whether to enable tracing
        
    Returns:
        True if setup successful
    """
    service = get_tracing_service()
    return service.initialize(
        api_key=api_key,
        project=project,
        enabled=enabled
    )