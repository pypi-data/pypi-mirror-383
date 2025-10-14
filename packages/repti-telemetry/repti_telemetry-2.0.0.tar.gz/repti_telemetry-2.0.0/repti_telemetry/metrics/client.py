"""
Prometheus metrics client for ReptiDex microservices.
"""

from typing import Optional

from prometheus_client import Counter, Gauge, Histogram


class MetricsClient:
    """
    Prometheus metrics client for tracking application metrics.

    Provides pre-configured metrics for common operations:
    - HTTP request metrics (latency, status codes, counts)
    - Business metrics (e.g., vivarium operations, animal operations)
    - System metrics (database connections, cache hits)

    Example:
        from repti_telemetry.metrics import MetricsClient

        metrics = MetricsClient(service_name="repti-core")

        # Track HTTP request
        with metrics.track_request_duration(endpoint="/api/vivariums", method="GET"):
            response = await get_vivariums()

        metrics.increment_request_count(endpoint="/api/vivariums", method="GET", status=200)
    """

    def __init__(self, service_name: str, namespace: str = "reptidex"):
        """
        Initialize metrics client.

        Args:
            service_name: Name of the service (e.g., "repti-core")
            namespace: Prometheus namespace for metrics (default: "reptidex")
        """
        self.service_name = service_name
        self.namespace = namespace

        # HTTP Request Metrics
        self.http_requests_total = Counter(
            name=f"{namespace}_http_requests_total",
            documentation="Total HTTP requests",
            labelnames=["service", "method", "endpoint", "status"],
        )

        self.http_request_duration_seconds = Histogram(
            name=f"{namespace}_http_request_duration_seconds",
            documentation="HTTP request duration in seconds",
            labelnames=["service", "method", "endpoint"],
            buckets=(
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
            ),
        )

        self.http_requests_in_progress = Gauge(
            name=f"{namespace}_http_requests_in_progress",
            documentation="HTTP requests currently in progress",
            labelnames=["service", "method", "endpoint"],
        )

        # Database Metrics
        self.db_connections_total = Gauge(
            name=f"{namespace}_db_connections_total",
            documentation="Total number of database connections",
            labelnames=["service", "state"],
        )

        self.db_query_duration_seconds = Histogram(
            name=f"{namespace}_db_query_duration_seconds",
            documentation="Database query duration in seconds",
            labelnames=["service", "operation"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        )

        # Cache Metrics
        self.cache_hits_total = Counter(
            name=f"{namespace}_cache_hits_total",
            documentation="Total cache hits",
            labelnames=["service", "cache_name"],
        )

        self.cache_misses_total = Counter(
            name=f"{namespace}_cache_misses_total",
            documentation="Total cache misses",
            labelnames=["service", "cache_name"],
        )

        # Business Metrics (ReptiDex-specific)
        self.vivarium_operations_total = Counter(
            name=f"{namespace}_vivarium_operations_total",
            documentation="Total vivarium operations",
            labelnames=["service", "operation", "status"],
        )

        self.animal_operations_total = Counter(
            name=f"{namespace}_animal_operations_total",
            documentation="Total animal operations",
            labelnames=["service", "operation", "status"],
        )

        # Error Metrics
        self.errors_total = Counter(
            name=f"{namespace}_errors_total",
            documentation="Total errors by type",
            labelnames=["service", "error_type", "endpoint"],
        )

    def increment_request_count(self, method: str, endpoint: str, status: int) -> None:
        """
        Increment HTTP request counter.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            status: HTTP status code
        """
        self.http_requests_total.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
            status=status,
        ).inc()

    def track_request_duration(self, method: str, endpoint: str) -> Histogram.time:
        """
        Context manager to track HTTP request duration.

        Args:
            method: HTTP method
            endpoint: API endpoint path

        Returns:
            Context manager for timing the request

        Example:
            with metrics.track_request_duration("GET", "/api/vivariums"):
                await process_request()
        """
        return self.http_request_duration_seconds.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
        ).time()

    def track_in_progress_request(
        self, method: str, endpoint: str
    ) -> Gauge.track_inprogress:
        """
        Context manager to track requests in progress.

        Args:
            method: HTTP method
            endpoint: API endpoint path

        Returns:
            Context manager for tracking in-progress requests
        """
        return self.http_requests_in_progress.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
        ).track_inprogress()

    def set_db_connections(self, state: str, count: int) -> None:
        """
        Set database connection gauge.

        Args:
            state: Connection state (active, idle, waiting)
            count: Number of connections
        """
        self.db_connections_total.labels(
            service=self.service_name,
            state=state,
        ).set(count)

    def track_db_query_duration(self, operation: str) -> Histogram.time:
        """
        Context manager to track database query duration.

        Args:
            operation: Database operation (select, insert, update, delete)

        Returns:
            Context manager for timing the query
        """
        return self.db_query_duration_seconds.labels(
            service=self.service_name,
            operation=operation,
        ).time()

    def increment_cache_hit(self, cache_name: str) -> None:
        """Increment cache hit counter."""
        self.cache_hits_total.labels(
            service=self.service_name,
            cache_name=cache_name,
        ).inc()

    def increment_cache_miss(self, cache_name: str) -> None:
        """Increment cache miss counter."""
        self.cache_misses_total.labels(
            service=self.service_name,
            cache_name=cache_name,
        ).inc()

    def increment_vivarium_operation(
        self, operation: str, status: str = "success"
    ) -> None:
        """
        Increment vivarium operation counter.

        Args:
            operation: Operation type (create, update, delete, etc.)
            status: Operation status (success, failure)
        """
        self.vivarium_operations_total.labels(
            service=self.service_name,
            operation=operation,
            status=status,
        ).inc()

    def increment_animal_operation(
        self, operation: str, status: str = "success"
    ) -> None:
        """
        Increment animal operation counter.

        Args:
            operation: Operation type (create, update, delete, etc.)
            status: Operation status (success, failure)
        """
        self.animal_operations_total.labels(
            service=self.service_name,
            operation=operation,
            status=status,
        ).inc()

    def increment_error(self, error_type: str, endpoint: Optional[str] = None) -> None:
        """
        Increment error counter.

        Args:
            error_type: Type of error (ValueError, DatabaseError, etc.)
            endpoint: Optional endpoint where error occurred
        """
        self.errors_total.labels(
            service=self.service_name,
            error_type=error_type,
            endpoint=endpoint or "unknown",
        ).inc()
