"""
Main logging setup and configuration.
"""

import logging
import sys

from repti_telemetry.logging.filters import create_pii_filter
from repti_telemetry.logging.formatter import create_formatter


def setup_logging(
    service_name: str,
    log_level: str = "INFO",
    enable_pii_filtering: bool = True,
    include_local_vars: bool = False,
    log_format: str = "json",
) -> None:
    """
    Configure structured JSON logging for the application.

    This should be called once at application startup before any logging occurs.

    Args:
        service_name: Name of the service (e.g., "repti-core")
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_pii_filtering: Enable automatic PII redaction
        include_local_vars: Include local variables in stack traces (use with caution)
        log_format: Log format ("json" or "text") - json recommended for Loki

    Example:
        setup_logging(
            service_name="repti-core",
            log_level="INFO",
            enable_pii_filtering=True,
        )
    """
    # Determine log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter
    if log_format == "json":
        formatter = create_formatter(
            service_name=service_name,
            include_local_vars=include_local_vars,
        )
    else:
        # Simple text formatter for development
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # Add PII filter if enabled
    if enable_pii_filtering:
        pii_filter = create_pii_filter()
        console_handler.addFilter(pii_filter)

    root_logger.addHandler(console_handler)

    # Configure third-party loggers to reduce noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("s3transfer").setLevel(logging.WARNING)

    # Configure uvicorn loggers if present
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.addHandler(console_handler)
        logger.setLevel(numeric_level)
        logger.propagate = False

    # Log successful setup
    root_logger.info(
        "Logging configured",
        extra={
            "service": service_name,
            "log_level": log_level,
            "log_format": log_format,
            "pii_filtering": enable_pii_filtering,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Name for the logger (typically __name__)

    Returns:
        Configured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Processing request", extra={"user_id": user.id})
    """
    return logging.getLogger(name)


def configure_sqlalchemy_logging(
    debug: bool = False,
    echo_pool: bool = False,
) -> None:
    """
    Configure SQLAlchemy logging levels.

    Args:
        debug: Enable debug-level logging for SQLAlchemy
        echo_pool: Enable connection pool logging

    Example:
        configure_sqlalchemy_logging(debug=True, echo_pool=True)
    """
    if debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    if echo_pool:
        logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)
    else:
        logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
