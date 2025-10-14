"""
ReptiDex Telemetry - Unified observability library for ReptiDex microservices.

This package provides logging, metrics, and tracing capabilities for ReptiDex services.
"""

from repti_telemetry.logging import (
    LogContext,
    animal_id_ctx,
    correlation_id_ctx,
    get_logger,
    request_id_ctx,
    session_id_ctx,
    setup_logging,
    transaction_id_ctx,
    user_id_ctx,
    vivarium_id_ctx,
)
from repti_telemetry.metrics import (
    MetricsClient,
    MetricsMiddleware,
    track_count,
    track_duration,
    track_errors,
    track_in_progress,
)

__version__ = "2.0.0"

__all__ = [
    # Logging
    "setup_logging",
    "get_logger",
    "LogContext",
    "request_id_ctx",
    "user_id_ctx",
    "session_id_ctx",
    "correlation_id_ctx",
    "vivarium_id_ctx",
    "animal_id_ctx",
    "transaction_id_ctx",
    # Metrics
    "MetricsClient",
    "MetricsMiddleware",
    "track_count",
    "track_duration",
    "track_errors",
    "track_in_progress",
]
