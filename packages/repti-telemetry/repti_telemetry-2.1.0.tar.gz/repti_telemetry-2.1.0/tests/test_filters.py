"""
Tests for PII filtering.
"""

import logging

import pytest

from repti_telemetry.logging.filters import PIIFilter


@pytest.fixture
def pii_filter():
    """Create a PIIFilter instance."""
    return PIIFilter()


def test_email_redaction(pii_filter):
    """Test email address redaction."""
    text = "Contact us at user@example.com for help"
    redacted = pii_filter.redact_pii(text)
    assert "user@example.com" not in redacted
    assert "@" in redacted  # Email structure preserved


def test_phone_redaction(pii_filter):
    """Test phone number redaction."""
    text = "Call me at 555-123-4567 or 5551234567"
    redacted = pii_filter.redact_pii(text)
    assert "555-123-4567" not in redacted
    assert "5551234567" not in redacted
    assert "***-***-****" in redacted


def test_credit_card_redaction(pii_filter):
    """Test credit card number redaction."""
    text = "Card number: 4532015112830366"
    redacted = pii_filter.redact_pii(text)
    assert "4532015112830366" not in redacted
    assert "****-****-****-****" in redacted


def test_ssn_redaction(pii_filter):
    """Test SSN redaction."""
    text = "SSN: 123-45-6789"
    redacted = pii_filter.redact_pii(text)
    assert "123-45-6789" not in redacted
    assert "***-**-****" in redacted


def test_bearer_token_redaction(pii_filter):
    """Test Bearer token redaction."""
    text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    redacted = pii_filter.redact_pii(text)
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in redacted
    assert "Bearer ***REDACTED***" in redacted


def test_api_key_redaction(pii_filter):
    """Test API key redaction."""
    text = "api_key=sk_live_1234567890abcdef"
    redacted = pii_filter.redact_pii(text)
    assert "sk_live_1234567890abcdef" not in redacted
    assert "***REDACTED***" in redacted


def test_password_redaction(pii_filter):
    """Test password redaction."""
    text = "Login with password: secret123"
    redacted = pii_filter.redact_pii(text)
    assert "secret123" not in redacted
    assert "***REDACTED***" in redacted


def test_aws_key_redaction(pii_filter):
    """Test AWS access key redaction."""
    text = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
    redacted = pii_filter.redact_pii(text)
    assert "AKIAIOSFODNN7EXAMPLE" not in redacted
    assert "AKIA***REDACTED***" in redacted


def test_dict_redaction(pii_filter):
    """Test dictionary field redaction."""
    data = {
        "username": "john_doe",
        "password": "secret123",
        "email": "john@example.com",
        "api_key": "sk_test_123",
    }
    redacted = pii_filter.redact_dict(data)

    assert redacted["username"] == "john_doe"  # Not sensitive
    assert redacted["password"] == "***REDACTED***"
    assert "john@example.com" not in redacted["email"]
    assert redacted["api_key"] == "***REDACTED***"


def test_nested_dict_redaction(pii_filter):
    """Test nested dictionary redaction."""
    data = {
        "user": {
            "name": "John Doe",
            "password": "secret",
            "contact": {"email": "john@example.com", "phone": "555-1234"},
        }
    }
    redacted = pii_filter.redact_dict(data)

    assert redacted["user"]["name"] == "John Doe"
    assert redacted["user"]["password"] == "***REDACTED***"
    assert "john@example.com" not in redacted["user"]["contact"]["email"]


def test_log_record_filtering(pii_filter):
    """Test filtering of log records."""
    # Create a log record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="User email is user@example.com",
        args=(),
        exc_info=None,
    )

    # Apply filter
    pii_filter.filter(record)

    # Check that email is redacted
    assert "user@example.com" not in record.msg
    assert "@" in record.msg  # Email structure preserved


def test_multiple_pii_types(pii_filter):
    """Test redaction of multiple PII types in one string."""
    text = "Contact john@example.com at 555-123-4567 with card 4532015112830366"
    redacted = pii_filter.redact_pii(text)

    assert "john@example.com" not in redacted
    assert "555-123-4567" not in redacted
    assert "4532015112830366" not in redacted
    assert "@" in redacted
    assert "***" in redacted
