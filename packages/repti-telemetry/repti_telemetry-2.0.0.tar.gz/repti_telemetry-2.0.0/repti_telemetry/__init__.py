"""
ReptiDex Telemetry - Unified observability library for ReptiDex microservices.

This package provides logging, metrics, and tracing capabilities for ReptiDex services.
"""

from repti_telemetry.logging import (
    LogContext,
    correlation_id_ctx,
    get_logger,
    request_id_ctx,
    session_id_ctx,
    setup_logging,
    user_id_ctx,
)

__version__ = "2.0.0"

__all__ = [
    "setup_logging",
    "get_logger",
    "LogContext",
    "request_id_ctx",
    "user_id_ctx",
    "session_id_ctx",
    "correlation_id_ctx",
]
