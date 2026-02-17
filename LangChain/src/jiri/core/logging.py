"""Structured logging configuration using Loguru.

Provides JSON-formatted logs for cloud-native observability.
Follows CODE_PATTERNS.md: JSON formatting with trace_id support.
"""

import sys
from typing import Any

from loguru import logger

from jiri.core.config import get_settings


def setup_logging() -> None:
    """Configure Loguru for the application.

    Sets up:
    - JSON formatting for production
    - Pretty formatting for development
    - Appropriate log levels
    - Request tracing support
    """
    settings = get_settings()

    # Remove default handler
    logger.remove()

    if settings.is_production:
        # JSON format for production (cloud-native)
        logger.add(
            sys.stdout,
            format="{message}",
            level=settings.log_level,
            serialize=True,  # JSON output
            backtrace=False,
            diagnose=False,
        )
    else:
        # Pretty format for development
        logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level=settings.log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )


def log_with_context(**context: Any) -> logger:  # type: ignore[valid-type]
    """Create a logger with bound context.

    Usage:
        log = log_with_context(trace_id="abc123", user_id="user1")
        log.info("Processing request")

    Args:
        **context: Key-value pairs to include in all log messages.

    Returns:
        Logger instance with bound context.
    """
    return logger.bind(**context)


class RequestLogger:
    """Middleware helper for request logging.

    Logs request/response with timing and trace IDs.
    """

    @staticmethod
    def log_request(
        method: str,
        path: str,
        trace_id: str,
        **extra: Any,
    ) -> None:
        """Log incoming request."""
        logger.bind(
            trace_id=trace_id,
            method=method,
            path=path,
            **extra,
        ).info("Request received")

    @staticmethod
    def log_response(
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        trace_id: str,
        **extra: Any,
    ) -> None:
        """Log outgoing response."""
        log = logger.bind(
            trace_id=trace_id,
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            **extra,
        )

        if status_code >= 500:
            log.error("Request failed")
        elif status_code >= 400:
            log.warning("Request error")
        else:
            log.info("Request completed")


# Re-export logger for convenience
__all__ = ["logger", "setup_logging", "log_with_context", "RequestLogger"]
