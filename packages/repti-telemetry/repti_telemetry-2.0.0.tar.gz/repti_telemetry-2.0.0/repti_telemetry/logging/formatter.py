"""
Enhanced JSON formatter with error fingerprinting and stack trace enhancement.
"""

import hashlib
import logging
import traceback
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger


def generate_error_fingerprint(
    error_type: str,
    error_message: str,
    file_name: Optional[str] = None,
    line_number: Optional[int] = None,
) -> str:
    """
    Generate a unique fingerprint for an error to enable grouping of similar errors.

    Args:
        error_type: Exception class name (e.g., "ValueError")
        error_message: Exception message
        file_name: File where the error occurred
        line_number: Line number where the error occurred

    Returns:
        SHA256 hash of the error signature
    """
    # Create a normalized error signature
    signature_parts = [error_type]

    # Normalize error message (remove dynamic parts like IDs, timestamps)
    normalized_message = error_message
    # Remove common dynamic patterns
    import re

    # UUIDs (must be before numbers)
    normalized_message = re.sub(
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
        "UUID",
        normalized_message,
        flags=re.IGNORECASE,
    )
    normalized_message = re.sub(r"\b\d+\b", "N", normalized_message)  # Numbers
    normalized_message = re.sub(
        r"\b\d{4}-\d{2}-\d{2}", "DATE", normalized_message
    )  # Dates

    signature_parts.append(normalized_message[:100])  # Limit message length

    # Add location info if available
    if file_name:
        signature_parts.append(file_name.split("/")[-1])  # Just the filename
    if line_number:
        signature_parts.append(f"L{line_number}")

    # Create hash
    signature = ":".join(signature_parts)
    return hashlib.sha256(signature.encode()).hexdigest()[:16]


class EnhancedJsonFormatter(jsonlogger.JsonFormatter):
    """
    Enhanced JSON formatter with comprehensive error tracking and context.

    Adds:
    - Standard ReptiDex fields (timestamp, level, service, etc.)
    - Error fingerprinting for grouping similar errors
    - Enhanced stack traces with local variables (optional)
    - Context variables (request_id, user_id, etc.)
    """

    def __init__(
        self,
        *args,
        service_name: str = "unknown",
        include_local_vars: bool = False,
        **kwargs,
    ):
        """
        Initialize the formatter.

        Args:
            service_name: Name of the service
            include_local_vars: Include local variables in stack traces (use with caution)
            *args: Passed to parent JsonFormatter
            **kwargs: Passed to parent JsonFormatter
        """
        self.service_name = service_name
        self.include_local_vars = include_local_vars
        super().__init__(*args, **kwargs)

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add custom fields to the log record."""
        super().add_fields(log_record, record, message_dict)

        # Standard fields
        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        log_record["level"] = record.levelname
        log_record["service"] = self.service_name
        log_record["logger"] = record.name

        # Add pathname and line number for debugging
        log_record["file"] = record.pathname
        log_record["line"] = record.lineno
        log_record["function"] = record.funcName

        # Import context variables here to avoid circular imports
        try:
            from repti_telemetry.logging.context import (
                endpoint_ctx,
                method_ctx,
                request_id_ctx,
                session_id_ctx,
                user_id_ctx,
            )

            # Add context variables if available
            request_id = request_id_ctx.get()
            if request_id:
                log_record["request_id"] = request_id

            user_id = user_id_ctx.get()
            if user_id:
                log_record["user_id"] = user_id

            session_id = session_id_ctx.get()
            if session_id:
                log_record["session_id"] = session_id

            endpoint = endpoint_ctx.get()
            if endpoint:
                log_record["endpoint"] = endpoint

            method = method_ctx.get()
            if method:
                log_record["method"] = method
        except ImportError:
            pass  # Context module not available

        # Handle exceptions with fingerprinting
        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info

            if exc_type and exc_value:
                error_type = exc_type.__name__
                error_message = str(exc_value)

                log_record["error_type"] = error_type
                log_record["error_message"] = error_message

                # Generate error fingerprint
                tb_info = traceback.extract_tb(exc_traceback)
                if tb_info:
                    last_frame = tb_info[-1]
                    fingerprint = generate_error_fingerprint(
                        error_type=error_type,
                        error_message=error_message,
                        file_name=last_frame.filename,
                        line_number=last_frame.lineno,
                    )
                    log_record["error_fingerprint"] = fingerprint

                    # Add error location
                    log_record["error_file"] = last_frame.filename
                    log_record["error_line"] = last_frame.lineno

                # Format stack trace
                if self.include_local_vars and exc_traceback:
                    # Include local variables (use with caution - may expose sensitive data)
                    stack_trace = "".join(
                        traceback.format_exception(exc_type, exc_value, exc_traceback)
                    )
                else:
                    # Standard stack trace without local variables
                    stack_trace = "".join(
                        traceback.format_exception(exc_type, exc_value, exc_traceback)
                    )

                log_record["stack_trace"] = stack_trace

        # Ensure message is always present
        if "message" not in log_record:
            log_record["message"] = record.getMessage()


def create_formatter(
    service_name: str,
    include_local_vars: bool = False,
    datefmt: str = "%Y-%m-%dT%H:%M:%S.%fZ",
) -> EnhancedJsonFormatter:
    """
    Create a configured EnhancedJsonFormatter instance.

    Args:
        service_name: Name of the service
        include_local_vars: Include local variables in stack traces
        datefmt: Date format string

    Returns:
        Configured formatter instance
    """
    return EnhancedJsonFormatter(
        fmt="%(timestamp)s %(level)s %(service)s %(logger)s %(message)s",
        datefmt=datefmt,
        service_name=service_name,
        include_local_vars=include_local_vars,
    )
