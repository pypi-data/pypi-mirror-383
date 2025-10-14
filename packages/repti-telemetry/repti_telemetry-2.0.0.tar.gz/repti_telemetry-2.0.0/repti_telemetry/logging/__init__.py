"""
ReptiDex Structured Logging Library

Provides structured JSON logging with PII filtering, error fingerprinting,
and context tracking for all ReptiDex microservices.
"""

__version__ = "2.0.0"

# Context management
from repti_telemetry.logging.context import (
    LogContext,
    animal_id_ctx,
    correlation_id_ctx,
    endpoint_ctx,
    get_current_context,
    method_ctx,
    request_id_ctx,
    session_id_ctx,
    transaction_id_ctx,
    user_id_ctx,
    vivarium_id_ctx,
)

# Decorators
from repti_telemetry.logging.decorators import log_endpoint, log_errors, log_performance

# Filters
from repti_telemetry.logging.filters import PIIFilter, create_pii_filter

# Formatter
from repti_telemetry.logging.formatter import (
    EnhancedJsonFormatter,
    create_formatter,
    generate_error_fingerprint,
)

# Core logging setup
from repti_telemetry.logging.setup import (
    configure_sqlalchemy_logging,
    get_logger,
    setup_logging,
)

# Try to import FastAPI middleware (optional)
try:
    from repti_telemetry.logging.middleware import RequestLoggingMiddleware

    __all_middleware__ = ["RequestLoggingMiddleware"]
except ImportError:
    __all_middleware__ = []

__all__ = [
    # Version
    "__version__",
    # Core setup
    "setup_logging",
    "get_logger",
    "configure_sqlalchemy_logging",
    # Context
    "LogContext",
    "get_current_context",
    "request_id_ctx",
    "correlation_id_ctx",
    "user_id_ctx",
    "session_id_ctx",
    "endpoint_ctx",
    "method_ctx",
    "vivarium_id_ctx",
    "animal_id_ctx",
    "transaction_id_ctx",
    # Decorators
    "log_endpoint",
    "log_errors",
    "log_performance",
    # Filters
    "PIIFilter",
    "create_pii_filter",
    # Formatter
    "EnhancedJsonFormatter",
    "create_formatter",
    "generate_error_fingerprint",
] + __all_middleware__
