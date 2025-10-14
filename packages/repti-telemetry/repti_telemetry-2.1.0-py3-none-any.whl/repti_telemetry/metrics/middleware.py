"""
FastAPI middleware for automatic Prometheus metrics collection.
"""

import time
from typing import Any, Callable, Optional

try:
    from fastapi import Request, Response
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import Response as StarletteResponse

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


if FASTAPI_AVAILABLE:
    from repti_telemetry.metrics.client import MetricsClient

    class MetricsMiddleware(BaseHTTPMiddleware):
        """
        Middleware that automatically collects Prometheus metrics for all requests.

        Features:
        - Tracks request count by method, endpoint, and status
        - Measures request duration
        - Tracks requests in progress
        - Provides /metrics endpoint for Prometheus scraping

        Example:
            from fastapi import FastAPI
            from repti_telemetry.metrics import MetricsMiddleware, MetricsClient

            app = FastAPI()
            metrics_client = MetricsClient(service_name="repti-core")
            app.add_middleware(MetricsMiddleware, metrics_client=metrics_client)
        """

        def __init__(
            self,
            app,
            metrics_client: MetricsClient,
            exclude_paths: Optional[list] = None,
        ):
            """
            Initialize the middleware.

            Args:
                app: FastAPI application
                metrics_client: MetricsClient instance
                exclude_paths: List of paths to exclude from metrics (e.g., ["/health", "/metrics"])
            """
            super().__init__(app)
            self.metrics_client = metrics_client
            self.exclude_paths = exclude_paths or [
                "/health",
                "/metrics",
                "/docs",
                "/redoc",
                "/openapi.json",
            ]

        async def dispatch(self, request: Request, call_next: Callable) -> Any:
            """
            Process the request and collect metrics.

            Args:
                request: The incoming HTTP request
                call_next: The next middleware/route handler

            Returns:
                The HTTP response
            """
            # Skip metrics collection for excluded paths
            if request.url.path in self.exclude_paths:
                return await call_next(request)

            method = request.method
            endpoint = request.url.path

            # Track request in progress
            with self.metrics_client.track_in_progress_request(
                method=method, endpoint=endpoint
            ):
                # Track request duration
                start_time = time.time()

                try:
                    # Process request
                    response = await call_next(request)
                    status_code = response.status_code

                    # Record metrics
                    duration = time.time() - start_time
                    self.metrics_client.increment_request_count(
                        method=method,
                        endpoint=endpoint,
                        status=status_code,
                    )

                    # Manually record duration (track_request_duration is a context manager)
                    self.metrics_client.http_request_duration_seconds.labels(
                        service=self.metrics_client.service_name,
                        method=method,
                        endpoint=endpoint,
                    ).observe(duration)

                    return response

                except Exception as exc:
                    # Record error metrics
                    duration = time.time() - start_time
                    self.metrics_client.increment_request_count(
                        method=method,
                        endpoint=endpoint,
                        status=500,
                    )
                    self.metrics_client.http_request_duration_seconds.labels(
                        service=self.metrics_client.service_name,
                        method=method,
                        endpoint=endpoint,
                    ).observe(duration)
                    self.metrics_client.increment_error(
                        error_type=type(exc).__name__,
                        endpoint=endpoint,
                    )
                    raise

    def setup_metrics_endpoint(app: Any, path: str = "/metrics") -> None:
        """
        Add a /metrics endpoint to the FastAPI app for Prometheus scraping.

        Args:
            app: FastAPI application
            path: Path for metrics endpoint (default: "/metrics")

        Example:
            from fastapi import FastAPI
            from repti_telemetry.metrics.middleware import setup_metrics_endpoint

            app = FastAPI()
            setup_metrics_endpoint(app)
        """

        @app.get(path, include_in_schema=False)
        async def metrics():
            """Prometheus metrics endpoint."""
            return StarletteResponse(
                content=generate_latest(),
                media_type=CONTENT_TYPE_LATEST,
            )

else:
    # Dummy middleware when FastAPI is not available
    class MetricsMiddleware:  # type: ignore
        """Dummy middleware when FastAPI is not installed."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError(
                "FastAPI is not installed. Install with: pip install repti-telemetry[metrics]"
            )

    def setup_metrics_endpoint(app: Any, path: str = "/metrics") -> None:
        """Dummy function when FastAPI is not available."""
        raise ImportError(
            "FastAPI is not installed. Install with: pip install repti-telemetry[metrics]"
        )
