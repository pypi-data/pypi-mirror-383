"""
Centralized Logging Configuration with Loki Integration
"""
import logging
import sys
import os
from typing import Optional

from ..config import settings


def setup_logger(
    name: str,
    level: Optional[str] = None,
    format_str: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger with centralized Loki integration

    Logs are sent to:
    1. Console (stdout) - For local development and debugging
    2. Loki (HTTP) - For centralized log aggregation (if enabled)

    Args:
        name: Logger name (e.g., "isA_Agent.API")
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: Log format string (optional)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Set log level
    log_level = (level or settings.log_level).upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Disable propagation to prevent duplicate logs
    logger.propagate = False

    # Log format
    formatter = logging.Formatter(format_str or settings.log_format)

    # 1. Console Handler (for local development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Loki Handler (for centralized logging)
    if settings.loki_enabled:
        try:
            import requests

            # Use custom Loki handler with immediate push (no buffering)
            class ImmediateLokiHandler(logging.Handler):
                """Custom Loki handler that pushes logs immediately without buffering"""

                def __init__(self, url, labels):
                    super().__init__()
                    self.url = url
                    self.labels = labels
                    self.session = requests.Session()

                def emit(self, record):
                    """Send log record immediately to Loki"""
                    try:
                        import time
                        # Format the log message
                        log_entry = self.format(record)

                        # Create Loki push payload
                        timestamp_ns = str(int(time.time() * 1e9))
                        payload = {
                            "streams": [{
                                "stream": self.labels,
                                "values": [[timestamp_ns, log_entry]]
                            }]
                        }

                        # Debug: print payload for first log
                        if not hasattr(self, '_debug_count'):
                            self._debug_count = 0
                        if self._debug_count == 0:
                            import json
                            print(f"[LOKI_DEBUG] First payload: {json.dumps(payload, indent=2)}", flush=True)
                            self._debug_count += 1

                        # Push immediately to Loki (non-blocking)
                        response = self.session.post(self.url, json=payload, timeout=2)

                        # Verify response
                        if self._debug_count < 3:
                            print(f"[LOKI_DEBUG] Response: status={response.status_code}, log='{log_entry[:80]}'", flush=True)
                            self._debug_count += 1
                    except Exception as e:
                        # Debug: print errors for first few attempts
                        if not hasattr(self, '_error_count'):
                            self._error_count = 0
                        if self._error_count < 3:
                            print(f"[LOKI_ERROR] Failed to push: {e}", flush=True)
                            import traceback
                            traceback.print_exc()
                            self._error_count += 1

            # Extract service name and logger component
            # e.g., "isA_Agent.API" -> service="agent", logger="API"
            service_name = "agent"
            logger_component = name.replace("isA_Agent.", "").replace("isA_Agent", "main")

            # Labels for Loki (used for filtering and searching)
            loki_labels = {
                "service": service_name,
                "logger": logger_component,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "job": "agent_service"
            }

            # Create custom Loki handler with immediate push
            loki_handler = ImmediateLokiHandler(
                url=f"{settings.loki_url}/loki/api/v1/push",
                labels=loki_labels
            )

            # Set formatter
            loki_handler.setFormatter(formatter)

            # Only send INFO and above to Loki (reduce network traffic)
            loki_handler.setLevel(logging.INFO)

            logger.addHandler(loki_handler)

            # Log successful Loki integration (only once)
            if name == "isA_Agent":
                logger.info(f"✅ Centralized logging enabled | loki_url={settings.loki_url}")

        except ImportError as e:
            # requests not installed
            if name == "isA_Agent":
                logger.warning(f"⚠️  Could not setup Loki handler: {e}")
        except Exception as e:
            # Loki unavailable or other error - don't fail the app
            if name == "isA_Agent":
                logger.warning(f"⚠️  Could not connect to Loki at {settings.loki_url}: {e}")
                logger.info("📝 Logging to console only")

    return logger


# Create default application loggers
app_logger = setup_logger("isA_Agent")
api_logger = setup_logger("isA_Agent.API")
agent_logger = setup_logger("isA_Agent.SmartAgent")
tracer_logger = setup_logger("isA_Agent.Tracer")
