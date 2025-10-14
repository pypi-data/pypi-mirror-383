"""
FastAPI middleware for request logging and context management.
"""

import time
import uuid
from typing import Callable, Optional

try:
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Create dummy classes for type hints when FastAPI is not installed
    class Request:  # type: ignore
        pass

    class Response:  # type: ignore
        pass

    class BaseHTTPMiddleware:  # type: ignore
        pass


from repti_telemetry.logging.context import (
    endpoint_ctx,
    method_ctx,
    request_id_ctx,
    session_id_ctx,
    user_id_ctx,
)
from repti_telemetry.logging.setup import get_logger

logger = get_logger(__name__)


if FASTAPI_AVAILABLE:

    class RequestLoggingMiddleware(BaseHTTPMiddleware):
        """
        Middleware that adds request ID to logging context and logs all requests.

        Features:
        - Generates or extracts correlation ID (X-Request-ID header)
        - Adds request context to all logs (request_id, user_id, endpoint, method)
        - Logs request start, completion, and errors
        - Tracks request duration
        - Returns correlation ID in response headers

        Example:
            from fastapi import FastAPI
            from repti_telemetry.logging.middleware import RequestLoggingMiddleware

            app = FastAPI()
            app.add_middleware(RequestLoggingMiddleware)
        """

        def __init__(
            self,
            app,
            log_request_body: bool = False,
            log_response_body: bool = False,
            exclude_paths: Optional[list] = None,
        ):
            """
            Initialize the middleware.

            Args:
                app: FastAPI application
                log_request_body: Log request body (use with caution)
                log_response_body: Log response body (use with caution)
                exclude_paths: List of paths to exclude from logging (e.g., ["/health", "/metrics"])
            """
            super().__init__(app)
            self.log_request_body = log_request_body
            self.log_response_body = log_response_body
            self.exclude_paths = exclude_paths or [
                "/health",
                "/metrics",
                "/docs",
                "/redoc",
                "/openapi.json",
            ]

        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            """
            Process the request and add logging context.

            Args:
                request: The incoming HTTP request
                call_next: The next middleware/route handler

            Returns:
                The HTTP response
            """
            # Skip logging for excluded paths
            if request.url.path in self.exclude_paths:
                return await call_next(request)

            # Generate or extract request ID
            request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

            # Extract user_id if present (from JWT token or session)
            user_id = None
            if hasattr(request.state, "user_id"):
                user_id = str(request.state.user_id)
            elif hasattr(request.state, "user"):
                user_id = str(getattr(request.state.user, "id", None))

            # Extract session_id if present
            session_id = request.headers.get("X-Session-ID")

            # Set context variables
            request_id_token = request_id_ctx.set(request_id)
            endpoint_token = endpoint_ctx.set(request.url.path)
            method_token = method_ctx.set(request.method)
            user_id_token = user_id_ctx.set(user_id) if user_id else None
            session_id_token = session_id_ctx.set(session_id) if session_id else None

            # Record start time
            start_time = time.time()

            # Build log context
            log_extra = {
                "method": request.method,
                "path": request.url.path,
                "query_params": (
                    dict(request.query_params) if request.query_params else None
                ),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }

            # Optionally log request body
            if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    if body:
                        # Decode and include (PII filter will redact sensitive data)
                        log_extra["request_body"] = body.decode("utf-8")[
                            :1000
                        ]  # Limit size
                except Exception:
                    pass  # Ignore body reading errors

            # Log request start
            logger.info("Request started", extra=log_extra)

            try:
                # Process request
                response = await call_next(request)

                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Log request completion
                logger.info(
                    "Request completed",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": round(duration_ms, 2),
                    },
                )

                # Add request ID to response headers
                response.headers["X-Request-ID"] = request_id

                return response

            except Exception as exc:
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Log request error
                logger.error(
                    "Request failed",
                    extra={
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": round(duration_ms, 2),
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                    },
                    exc_info=True,
                )
                raise

            finally:
                # Reset context variables
                request_id_ctx.reset(request_id_token)
                endpoint_ctx.reset(endpoint_token)
                method_ctx.reset(method_token)
                if user_id_token:
                    user_id_ctx.reset(user_id_token)
                if session_id_token:
                    session_id_ctx.reset(session_id_token)

else:
    # Dummy middleware when FastAPI is not available
    class RequestLoggingMiddleware:  # type: ignore
        """Dummy middleware when FastAPI is not installed."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "FastAPI is not installed. Install with: pip install repti-logging[fastapi]"
            )
