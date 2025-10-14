"""
Tests for context management.
"""

import pytest

from repti_telemetry.logging.context import (
    LogContext,
    endpoint_ctx,
    get_current_context,
    method_ctx,
    request_id_ctx,
    session_id_ctx,
    user_id_ctx,
)


def test_log_context_basic():
    """Test basic context setting."""
    # Initially no context
    assert request_id_ctx.get() is None
    assert user_id_ctx.get() is None

    # Set context
    with LogContext(request_id="req123", user_id="user456"):
        assert request_id_ctx.get() == "req123"
        assert user_id_ctx.get() == "user456"

    # Context cleared after exiting
    assert request_id_ctx.get() is None
    assert user_id_ctx.get() is None


def test_log_context_nested():
    """Test nested context managers."""
    with LogContext(request_id="req123"):
        assert request_id_ctx.get() == "req123"

        with LogContext(user_id="user456"):
            # Both contexts active
            assert request_id_ctx.get() == "req123"
            assert user_id_ctx.get() == "user456"

        # Inner context cleared
        assert request_id_ctx.get() == "req123"
        assert user_id_ctx.get() is None

    # All contexts cleared
    assert request_id_ctx.get() is None


def test_log_context_all_fields():
    """Test setting all context fields."""
    with LogContext(
        request_id="req123",
        user_id="user456",
        session_id="sess789",
        endpoint="/api/v1/users",
        method="GET",
        vivarium_id="viv123",
        animal_id="animal456",
        transaction_id="txn789",
    ):
        assert request_id_ctx.get() == "req123"
        assert user_id_ctx.get() == "user456"
        assert session_id_ctx.get() == "sess789"
        assert endpoint_ctx.get() == "/api/v1/users"
        assert method_ctx.get() == "GET"

    # All cleared
    assert request_id_ctx.get() is None
    assert user_id_ctx.get() is None


def test_get_current_context_empty():
    """Test getting current context when empty."""
    context = get_current_context()
    assert context == {}


def test_get_current_context_with_values():
    """Test getting current context with values."""
    with LogContext(request_id="req123", user_id="user456"):
        context = get_current_context()
        assert context["request_id"] == "req123"
        assert context["user_id"] == "user456"
        assert len(context) == 2


def test_log_context_partial():
    """Test setting only some context fields."""
    with LogContext(request_id="req123"):
        context = get_current_context()
        assert "request_id" in context
        assert "user_id" not in context


@pytest.mark.asyncio
async def test_context_async_propagation():
    """Test that context propagates across async boundaries."""

    async def inner_function():
        # Context should be accessible here
        return request_id_ctx.get()

    with LogContext(request_id="req123"):
        result = await inner_function()
        assert result == "req123"
