"""
Context variables for tracking request/user context across async boundaries.
"""

from contextvars import ContextVar
from typing import Optional

# Context variables for tracking across async boundaries
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)
user_id_ctx: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
session_id_ctx: ContextVar[Optional[str]] = ContextVar("session_id", default=None)
endpoint_ctx: ContextVar[Optional[str]] = ContextVar("endpoint", default=None)
method_ctx: ContextVar[Optional[str]] = ContextVar("method", default=None)

# Additional domain-specific context variables
vivarium_id_ctx: ContextVar[Optional[str]] = ContextVar("vivarium_id", default=None)
animal_id_ctx: ContextVar[Optional[str]] = ContextVar("animal_id", default=None)
transaction_id_ctx: ContextVar[Optional[str]] = ContextVar(
    "transaction_id", default=None
)


class LogContext:
    """
    Context manager for setting logging context variables.

    Example:
        async def process_request(request_id: str, user_id: str):
            with LogContext(request_id=request_id, user_id=user_id):
                logger.info("Processing request")  # Includes request_id and user_id
                await some_operation()
                logger.info("Request completed")  # Also includes context
    """

    def __init__(
        self,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        vivarium_id: Optional[str] = None,
        animal_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
    ):
        """
        Initialize context manager with optional context values.

        Args:
            request_id: Request correlation ID
            correlation_id: Cross-service correlation ID
            user_id: Authenticated user ID
            session_id: Session ID
            endpoint: API endpoint path
            method: HTTP method
            vivarium_id: Vivarium (enclosure) ID
            animal_id: Animal ID
            transaction_id: Transaction ID for commerce operations
        """
        self.request_id = request_id
        self.correlation_id = correlation_id
        self.user_id = user_id
        self.session_id = session_id
        self.endpoint = endpoint
        self.method = method
        self.vivarium_id = vivarium_id
        self.animal_id = animal_id
        self.transaction_id = transaction_id
        self.tokens = []

    def __enter__(self):
        """Set context variables."""
        if self.request_id is not None:
            self.tokens.append(request_id_ctx.set(self.request_id))
        if self.correlation_id is not None:
            self.tokens.append(correlation_id_ctx.set(self.correlation_id))
        if self.user_id is not None:
            self.tokens.append(user_id_ctx.set(self.user_id))
        if self.session_id is not None:
            self.tokens.append(session_id_ctx.set(self.session_id))
        if self.endpoint is not None:
            self.tokens.append(endpoint_ctx.set(self.endpoint))
        if self.method is not None:
            self.tokens.append(method_ctx.set(self.method))
        if self.vivarium_id is not None:
            self.tokens.append(vivarium_id_ctx.set(self.vivarium_id))
        if self.animal_id is not None:
            self.tokens.append(animal_id_ctx.set(self.animal_id))
        if self.transaction_id is not None:
            self.tokens.append(transaction_id_ctx.set(self.transaction_id))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Reset context variables."""
        for token in reversed(self.tokens):
            if hasattr(token, "var"):
                token.var.reset(token)


def get_current_context() -> dict:
    """
    Get all current context values as a dictionary.

    Returns:
        Dictionary of context variable names to values
    """
    context = {}

    request_id = request_id_ctx.get()
    if request_id:
        context["request_id"] = request_id

    correlation_id = correlation_id_ctx.get()
    if correlation_id:
        context["correlation_id"] = correlation_id

    user_id = user_id_ctx.get()
    if user_id:
        context["user_id"] = user_id

    session_id = session_id_ctx.get()
    if session_id:
        context["session_id"] = session_id

    endpoint = endpoint_ctx.get()
    if endpoint:
        context["endpoint"] = endpoint

    method = method_ctx.get()
    if method:
        context["method"] = method

    vivarium_id = vivarium_id_ctx.get()
    if vivarium_id:
        context["vivarium_id"] = vivarium_id

    animal_id = animal_id_ctx.get()
    if animal_id:
        context["animal_id"] = animal_id

    transaction_id = transaction_id_ctx.get()
    if transaction_id:
        context["transaction_id"] = transaction_id

    return context
