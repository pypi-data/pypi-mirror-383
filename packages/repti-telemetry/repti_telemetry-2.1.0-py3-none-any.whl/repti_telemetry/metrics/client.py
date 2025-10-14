"""
Prometheus metrics client for ReptiDex microservices.
"""

from typing import Any, Optional

from prometheus_client import Counter, Gauge, Histogram, Info


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

    def __init__(
        self,
        service_name: str,
        namespace: str = "reptidex",
        version: str = "unknown",
        environment: str = "unknown",
    ):
        """
        Initialize metrics client.

        Args:
            service_name: Name of the service (e.g., "repti-core")
            namespace: Prometheus namespace for metrics (default: "reptidex")
            version: Service version (default: "unknown")
            environment: Deployment environment (default: "unknown")
        """
        self.service_name = service_name
        self.namespace = namespace
        self.version = version
        self.environment = environment

        # Service Information
        self.service_info = Info(
            name=f"{namespace}_service",
            documentation="Service information",
        )
        self.service_info.info(
            {
                "name": service_name,
                "version": version,
                "environment": environment,
            }
        )

        # HTTP Request Metrics
        self.http_requests_total = Counter(
            name=f"{namespace}_http_requests_total",
            documentation="Total HTTP requests",
            labelnames=["service", "method", "endpoint", "status"],
        )

        self.http_request_duration_seconds = Histogram(
            name=f"{namespace}_http_request_duration_seconds",
            documentation="HTTP request duration in seconds",
            labelnames=["service", "method", "endpoint", "category"],
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

        # SLA and Performance Tracking Metrics
        self.endpoint_sla_violations_total = Counter(
            name=f"{namespace}_endpoint_sla_violations_total",
            documentation="Total number of SLA violations per endpoint",
            labelnames=["service", "method", "endpoint", "category"],
        )

        self.endpoint_performance_degraded = Gauge(
            name=f"{namespace}_endpoint_performance_degraded",
            documentation="Indicates if endpoint is experiencing performance degradation (1=degraded, 0=normal)",
            labelnames=["service", "method", "endpoint", "category"],
        )

        # Health Check Metrics
        self.health_check_duration_seconds = Histogram(
            name=f"{namespace}_health_check_duration_seconds",
            documentation="Duration of health check operations",
            labelnames=["service", "check_type", "dependency"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        )

        self.health_check_failures_total = Counter(
            name=f"{namespace}_health_check_failures_total",
            documentation="Total number of health check failures",
            labelnames=["service", "dependency", "error_type"],
        )

        self.health_check_status = Gauge(
            name=f"{namespace}_health_check_status",
            documentation="Current health check status (1=healthy, 0=unhealthy)",
            labelnames=["service", "dependency"],
        )

        # Database Connection Pool Metrics
        self.database_connections_total = Gauge(
            name=f"{namespace}_database_connections_total",
            documentation="Total number of database connections in the pool",
            labelnames=["service"],
        )

        self.database_connections_in_use = Gauge(
            name=f"{namespace}_database_connections_in_use",
            documentation="Number of database connections currently in use",
            labelnames=["service"],
        )

        # User/Active Session Metrics
        self.active_users = Gauge(
            name=f"{namespace}_active_users",
            documentation="Number of currently active users",
            labelnames=["service"],
        )

        self.users_registered_total = Counter(
            name=f"{namespace}_users_registered_total",
            documentation="Total number of users registered",
            labelnames=["service"],
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

    def track_request_duration(
        self, method: str, endpoint: str, category: str = "default"
    ) -> Any:
        """
        Context manager to track HTTP request duration.

        Args:
            method: HTTP method
            endpoint: API endpoint path
            category: Performance category (health, read, write, complex, default)

        Returns:
            Context manager for timing the request

        Example:
            with metrics.track_request_duration("GET", "/api/vivariums", "read"):
                await process_request()
        """
        return self.http_request_duration_seconds.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
            category=category,
        ).time()

    def track_in_progress_request(self, method: str, endpoint: str) -> Any:
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

    def track_db_query_duration(self, operation: str) -> Any:
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

    # SLA and Performance Methods

    def increment_sla_violation(
        self, method: str, endpoint: str, category: str = "default"
    ) -> None:
        """
        Increment SLA violation counter.

        Args:
            method: HTTP method
            endpoint: API endpoint path
            category: Performance category
        """
        self.endpoint_sla_violations_total.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
            category=category,
        ).inc()

    def set_performance_degraded(
        self, method: str, endpoint: str, category: str, degraded: bool
    ) -> None:
        """
        Set performance degradation flag for an endpoint.

        Args:
            method: HTTP method
            endpoint: API endpoint path
            category: Performance category
            degraded: True if degraded, False if normal
        """
        self.endpoint_performance_degraded.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
            category=category,
        ).set(1 if degraded else 0)

    # Health Check Methods

    def track_health_check_duration(self, check_type: str, dependency: str) -> Any:
        """
        Context manager to track health check duration.

        Args:
            check_type: Type of health check (ready, live, deep)
            dependency: Dependency being checked (database, redis, etc.)

        Returns:
            Context manager for timing the health check
        """
        return self.health_check_duration_seconds.labels(
            service=self.service_name,
            check_type=check_type,
            dependency=dependency,
        ).time()

    def increment_health_check_failure(self, dependency: str, error_type: str) -> None:
        """
        Increment health check failure counter.

        Args:
            dependency: Dependency that failed (database, redis, etc.)
            error_type: Type of error
        """
        self.health_check_failures_total.labels(
            service=self.service_name,
            dependency=dependency,
            error_type=error_type,
        ).inc()

    def set_health_check_status(self, dependency: str, healthy: bool) -> None:
        """
        Set health check status for a dependency.

        Args:
            dependency: Dependency name (database, redis, etc.)
            healthy: True if healthy, False if unhealthy
        """
        self.health_check_status.labels(
            service=self.service_name,
            dependency=dependency,
        ).set(1 if healthy else 0)

    # Database Connection Pool Methods

    def set_database_connections_total(self, count: int) -> None:
        """
        Set total database connections gauge.

        Args:
            count: Total number of connections in the pool
        """
        self.database_connections_total.labels(
            service=self.service_name,
        ).set(count)

    def set_database_connections_in_use(self, count: int) -> None:
        """
        Set database connections in use gauge.

        Args:
            count: Number of connections currently in use
        """
        self.database_connections_in_use.labels(
            service=self.service_name,
        ).set(count)

    # User Metrics Methods

    def set_active_users(self, count: int) -> None:
        """
        Set active users gauge.

        Args:
            count: Number of currently active users
        """
        self.active_users.labels(
            service=self.service_name,
        ).set(count)

    def increment_user_registration(self) -> None:
        """Increment user registration counter."""
        self.users_registered_total.labels(
            service=self.service_name,
        ).inc()

    # Generic Business Metric Methods

    def create_counter(
        self, name: str, documentation: str, labelnames: Optional[list] = None
    ) -> Counter:
        """
        Create a custom counter metric.

        Args:
            name: Metric name (will be prefixed with namespace)
            documentation: Metric description
            labelnames: Optional list of label names

        Returns:
            Counter metric instance
        """
        return Counter(
            name=f"{self.namespace}_{name}",
            documentation=documentation,
            labelnames=labelnames or [],
        )

    def create_gauge(
        self, name: str, documentation: str, labelnames: Optional[list] = None
    ) -> Gauge:
        """
        Create a custom gauge metric.

        Args:
            name: Metric name (will be prefixed with namespace)
            documentation: Metric description
            labelnames: Optional list of label names

        Returns:
            Gauge metric instance
        """
        return Gauge(
            name=f"{self.namespace}_{name}",
            documentation=documentation,
            labelnames=labelnames or [],
        )

    def create_histogram(
        self,
        name: str,
        documentation: str,
        labelnames: Optional[list] = None,
        buckets: Optional[tuple] = None,
    ) -> Histogram:
        """
        Create a custom histogram metric.

        Args:
            name: Metric name (will be prefixed with namespace)
            documentation: Metric description
            labelnames: Optional list of label names
            buckets: Optional custom buckets for histogram

        Returns:
            Histogram metric instance
        """
        if buckets:
            return Histogram(
                name=f"{self.namespace}_{name}",
                documentation=documentation,
                labelnames=labelnames or [],
                buckets=buckets,
            )
        return Histogram(
            name=f"{self.namespace}_{name}",
            documentation=documentation,
            labelnames=labelnames or [],
        )
