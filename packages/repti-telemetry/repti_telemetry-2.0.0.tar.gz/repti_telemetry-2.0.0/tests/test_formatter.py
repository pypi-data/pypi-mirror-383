"""
Tests for enhanced JSON formatter.
"""

import json
import logging

from repti_telemetry.logging.formatter import (
    EnhancedJsonFormatter,
    generate_error_fingerprint,
)


def test_generate_error_fingerprint():
    """Test error fingerprint generation."""
    fingerprint1 = generate_error_fingerprint(
        error_type="ValueError",
        error_message="Invalid value: 123",
        file_name="test.py",
        line_number=42,
    )

    # Should be a 16-character hex string
    assert len(fingerprint1) == 16
    assert all(c in "0123456789abcdef" for c in fingerprint1)

    # Same error should generate same fingerprint
    fingerprint2 = generate_error_fingerprint(
        error_type="ValueError",
        error_message="Invalid value: 123",
        file_name="test.py",
        line_number=42,
    )
    assert fingerprint1 == fingerprint2

    # Different error should generate different fingerprint
    fingerprint3 = generate_error_fingerprint(
        error_type="KeyError",
        error_message="Key not found",
        file_name="test.py",
        line_number=42,
    )
    assert fingerprint1 != fingerprint3


def test_fingerprint_normalization():
    """Test that fingerprints normalize dynamic values."""
    # Different IDs should produce same fingerprint
    fingerprint1 = generate_error_fingerprint(
        error_type="ValueError", error_message="User 123 not found"
    )
    fingerprint2 = generate_error_fingerprint(
        error_type="ValueError", error_message="User 456 not found"
    )
    assert fingerprint1 == fingerprint2

    # Different UUIDs should produce same fingerprint
    fingerprint3 = generate_error_fingerprint(
        error_type="ValueError",
        error_message="ID 550e8400-e29b-41d4-a716-446655440000 not found",
    )
    fingerprint4 = generate_error_fingerprint(
        error_type="ValueError",
        error_message="ID 6ba7b810-9dad-11d1-80b4-00c04fd430c8 not found",
    )
    assert fingerprint3 == fingerprint4


def test_formatter_basic_fields():
    """Test that formatter adds all basic fields."""
    formatter = EnhancedJsonFormatter(
        service_name="test-service",
        datefmt="%Y-%m-%dT%H:%M:%S.%fZ",
    )

    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="/app/test.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)
    log_data = json.loads(formatted)

    assert log_data["level"] == "INFO"
    assert log_data["service"] == "test-service"
    assert log_data["logger"] == "test.logger"
    assert log_data["message"] == "Test message"
    assert log_data["file"] == "/app/test.py"
    assert log_data["line"] == 42
    assert "timestamp" in log_data


def test_formatter_with_exception():
    """Test formatter with exception information."""
    formatter = EnhancedJsonFormatter(service_name="test-service")

    try:
        raise ValueError("Test error")
    except ValueError:
        import sys

        exc_info = sys.exc_info()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="/app/test.py",
            lineno=42,
            msg="An error occurred",
            args=(),
            exc_info=exc_info,
        )

    formatted = formatter.format(record)
    log_data = json.loads(formatted)

    assert log_data["level"] == "ERROR"
    assert log_data["error_type"] == "ValueError"
    assert log_data["error_message"] == "Test error"
    assert "error_fingerprint" in log_data
    assert "stack_trace" in log_data
    assert "ValueError: Test error" in log_data["stack_trace"]
    assert "error_file" in log_data
    assert "error_line" in log_data


def test_formatter_json_serialization():
    """Test that formatter produces valid JSON."""
    formatter = EnhancedJsonFormatter(service_name="test-service")

    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="/app/test.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)

    # Should be valid JSON
    log_data = json.loads(formatted)
    assert isinstance(log_data, dict)
    assert "message" in log_data


def test_formatter_with_extra_fields():
    """Test formatter with extra fields."""
    formatter = EnhancedJsonFormatter(service_name="test-service")

    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="/app/test.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Add extra fields
    record.user_id = "user123"
    record.request_id = "req456"

    formatted = formatter.format(record)
    log_data = json.loads(formatted)

    # Extra fields should not interfere with standard fields
    assert log_data["message"] == "Test message"
    assert log_data["service"] == "test-service"
