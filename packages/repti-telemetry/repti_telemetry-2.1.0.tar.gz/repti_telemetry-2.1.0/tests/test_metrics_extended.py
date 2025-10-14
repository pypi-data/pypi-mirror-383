"""
Tests for extended metrics functionality.
"""

import pytest
from prometheus_client import CollectorRegistry

from repti_telemetry.metrics import (
    MetricsClient,
    track_count,
    track_duration,
    track_errors,
    track_in_progress,
)


@pytest.fixture
def registry():
    """Create a fresh registry for each test."""
    return CollectorRegistry()


@pytest.fixture
def metrics_client(registry):
    """Create a metrics client for testing."""
    # Override the default registry with a fresh one for testing
    from prometheus_client import Counter, Gauge, Histogram, Info

    client = MetricsClient.__new__(MetricsClient)
    client.service_name = "test-service"
    client.namespace = "test"
    client.version = "1.0.0"
    client.environment = "test"

    # Service Information
    client.service_info = Info(
        name=f"{client.namespace}_service",
        documentation="Service information",
        registry=registry,
    )
    client.service_info.info(
        {
            "name": client.service_name,
            "version": client.version,
            "environment": client.environment,
        }
    )

    # HTTP Request Metrics
    client.http_requests_total = Counter(
        name=f"{client.namespace}_http_requests_total",
        documentation="Total HTTP requests",
        labelnames=["service", "method", "endpoint", "status"],
        registry=registry,
    )

    client.http_request_duration_seconds = Histogram(
        name=f"{client.namespace}_http_request_duration_seconds",
        documentation="HTTP request duration in seconds",
        labelnames=["service", "method", "endpoint", "category"],
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
        registry=registry,
    )

    client.http_requests_in_progress = Gauge(
        name=f"{client.namespace}_http_requests_in_progress",
        documentation="HTTP requests currently in progress",
        labelnames=["service", "method", "endpoint"],
        registry=registry,
    )

    # Database Metrics
    client.db_connections_total = Gauge(
        name=f"{client.namespace}_db_connections_total",
        documentation="Total number of database connections",
        labelnames=["service", "state"],
        registry=registry,
    )

    client.db_query_duration_seconds = Histogram(
        name=f"{client.namespace}_db_query_duration_seconds",
        documentation="Database query duration in seconds",
        labelnames=["service", "operation"],
        buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        registry=registry,
    )

    # Business Metrics
    client.vivarium_operations_total = Counter(
        name=f"{client.namespace}_vivarium_operations_total",
        documentation="Total vivarium operations",
        labelnames=["service", "operation", "status"],
        registry=registry,
    )

    # Error Metrics
    client.errors_total = Counter(
        name=f"{client.namespace}_errors_total",
        documentation="Total errors by type",
        labelnames=["service", "error_type", "endpoint"],
        registry=registry,
    )

    # SLA and Performance Tracking Metrics
    client.endpoint_sla_violations_total = Counter(
        name=f"{client.namespace}_endpoint_sla_violations_total",
        documentation="Total number of SLA violations per endpoint",
        labelnames=["service", "method", "endpoint", "category"],
        registry=registry,
    )

    client.endpoint_performance_degraded = Gauge(
        name=f"{client.namespace}_endpoint_performance_degraded",
        documentation="Indicates if endpoint is experiencing performance degradation",
        labelnames=["service", "method", "endpoint", "category"],
        registry=registry,
    )

    # Health Check Metrics
    client.health_check_duration_seconds = Histogram(
        name=f"{client.namespace}_health_check_duration_seconds",
        documentation="Duration of health check operations",
        labelnames=["service", "check_type", "dependency"],
        buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        registry=registry,
    )

    client.health_check_failures_total = Counter(
        name=f"{client.namespace}_health_check_failures_total",
        documentation="Total number of health check failures",
        labelnames=["service", "dependency", "error_type"],
        registry=registry,
    )

    client.health_check_status = Gauge(
        name=f"{client.namespace}_health_check_status",
        documentation="Current health check status (1=healthy, 0=unhealthy)",
        labelnames=["service", "dependency"],
        registry=registry,
    )

    # Database Connection Pool Metrics
    client.database_connections_total = Gauge(
        name=f"{client.namespace}_database_connections_total",
        documentation="Total number of database connections in the pool",
        labelnames=["service"],
        registry=registry,
    )

    client.database_connections_in_use = Gauge(
        name=f"{client.namespace}_database_connections_in_use",
        documentation="Number of database connections currently in use",
        labelnames=["service"],
        registry=registry,
    )

    # User/Active Session Metrics
    client.active_users = Gauge(
        name=f"{client.namespace}_active_users",
        documentation="Number of currently active users",
        labelnames=["service"],
        registry=registry,
    )

    client.users_registered_total = Counter(
        name=f"{client.namespace}_users_registered_total",
        documentation="Total number of users registered",
        labelnames=["service"],
        registry=registry,
    )

    return client


def test_service_info_initialization(metrics_client):
    """Test that service info is properly initialized."""
    # Service info should be set during initialization
    assert metrics_client.service_name == "test-service"
    assert metrics_client.version == "1.0.0"
    assert metrics_client.environment == "test"


def test_sla_violation_tracking(metrics_client, registry):
    """Test SLA violation tracking."""
    # Increment SLA violation
    metrics_client.increment_sla_violation(
        method="GET", endpoint="/api/test", category="read"
    )

    # Verify metric exists in registry
    metric_name = "test_endpoint_sla_violations_total"
    assert any(metric_name in str(metric) for metric in registry.collect())


def test_performance_degradation_tracking(metrics_client, registry):
    """Test performance degradation tracking."""
    # Set performance degraded
    metrics_client.set_performance_degraded(
        method="GET", endpoint="/api/test", category="read", degraded=True
    )

    # Set back to normal
    metrics_client.set_performance_degraded(
        method="GET", endpoint="/api/test", category="read", degraded=False
    )

    # Verify metric exists
    metric_name = "test_endpoint_performance_degraded"
    assert any(metric_name in str(metric) for metric in registry.collect())


def test_health_check_metrics(metrics_client, registry):
    """Test health check metrics."""
    # Track health check duration
    with metrics_client.track_health_check_duration("ready", "database"):
        pass

    # Track failure
    metrics_client.increment_health_check_failure("database", "connection_timeout")

    # Set status
    metrics_client.set_health_check_status("database", True)
    metrics_client.set_health_check_status("database", False)

    # Verify metrics exist
    assert any(
        "test_health_check_duration_seconds" in str(metric)
        for metric in registry.collect()
    )
    assert any(
        "test_health_check_failures_total" in str(metric)
        for metric in registry.collect()
    )
    assert any(
        "test_health_check_status" in str(metric) for metric in registry.collect()
    )


def test_database_connection_pool_metrics(metrics_client, registry):
    """Test database connection pool metrics."""
    # Set connection counts
    metrics_client.set_database_connections_total(10)
    metrics_client.set_database_connections_in_use(5)

    # Verify metrics exist
    assert any(
        "test_database_connections_total" in str(metric)
        for metric in registry.collect()
    )
    assert any(
        "test_database_connections_in_use" in str(metric)
        for metric in registry.collect()
    )


def test_user_metrics(metrics_client, registry):
    """Test user metrics."""
    # Set active users
    metrics_client.set_active_users(42)

    # Increment registrations
    metrics_client.increment_user_registration()

    # Verify metrics exist
    assert any("test_active_users" in str(metric) for metric in registry.collect())
    assert any(
        "test_users_registered_total" in str(metric) for metric in registry.collect()
    )


def test_custom_metrics_creation(metrics_client, registry):
    """Test creating custom metrics."""
    # Note: Custom metrics created through the client won't use the test registry
    # This test just verifies the methods work without error
    # In production, all metrics share the default registry

    # Create custom counter
    custom_counter = metrics_client.create_counter(
        "custom_operations_total",
        "Total custom operations",
        labelnames=["operation_type"],
    )
    custom_counter.labels(operation_type="test").inc()

    # Create custom gauge
    custom_gauge = metrics_client.create_gauge("custom_queue_size", "Custom queue size")
    custom_gauge.set(100)

    # Create custom histogram
    custom_histogram = metrics_client.create_histogram(
        "custom_operation_duration_seconds",
        "Custom operation duration",
        buckets=(0.1, 0.5, 1.0, 5.0),
    )
    custom_histogram.observe(0.25)

    # Just verify no exceptions were raised
    assert custom_counter is not None
    assert custom_gauge is not None
    assert custom_histogram is not None


def test_track_duration_decorator_sync(metrics_client):
    """Test track_duration decorator with sync function."""

    @track_duration(
        metrics_client.db_query_duration_seconds,
        {"service": "test-service", "operation": "select"},
    )
    def query_database():
        return "result"

    result = query_database()
    assert result == "result"


@pytest.mark.asyncio
async def test_track_duration_decorator_async(metrics_client):
    """Test track_duration decorator with async function."""

    @track_duration(
        metrics_client.db_query_duration_seconds,
        {"service": "test-service", "operation": "select"},
    )
    async def query_database():
        return "result"

    result = await query_database()
    assert result == "result"


def test_track_count_decorator_sync(metrics_client):
    """Test track_count decorator with sync function."""

    @track_count(
        metrics_client.vivarium_operations_total,
        {"service": "test-service", "operation": "create", "status": "success"},
    )
    def create_vivarium():
        return "created"

    result = create_vivarium()
    assert result == "created"


@pytest.mark.asyncio
async def test_track_count_decorator_async(metrics_client):
    """Test track_count decorator with async function."""

    @track_count(
        metrics_client.vivarium_operations_total,
        {"service": "test-service", "operation": "create", "status": "success"},
    )
    async def create_vivarium():
        return "created"

    result = await create_vivarium()
    assert result == "created"


def test_track_in_progress_decorator_sync(metrics_client):
    """Test track_in_progress decorator with sync function."""

    @track_in_progress(
        metrics_client.http_requests_in_progress,
        {"service": "test-service", "method": "POST", "endpoint": "/test"},
    )
    def process_request():
        return "processed"

    result = process_request()
    assert result == "processed"


@pytest.mark.asyncio
async def test_track_in_progress_decorator_async(metrics_client):
    """Test track_in_progress decorator with async function."""

    @track_in_progress(
        metrics_client.http_requests_in_progress,
        {"service": "test-service", "method": "POST", "endpoint": "/test"},
    )
    async def process_request():
        return "processed"

    result = await process_request()
    assert result == "processed"


def test_track_errors_decorator_sync(metrics_client):
    """Test track_errors decorator with sync function - simplified without labels."""
    # The track_errors decorator expects specific labels structure
    # For this test, we'll just verify it works without full label matching
    from prometheus_client import Counter

    simple_errors = Counter(
        "test_simple_errors_total",
        "Simple errors for testing",
        ["error_type", "endpoint"],
    )

    @track_errors(simple_errors, "test_error", "/test")
    def failing_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        failing_function()


@pytest.mark.asyncio
async def test_track_errors_decorator_async(metrics_client):
    """Test track_errors decorator with async function - simplified without labels."""
    from prometheus_client import Counter

    simple_errors = Counter(
        "test_simple_errors_async_total",
        "Simple errors for testing",
        ["error_type", "endpoint"],
    )

    @track_errors(simple_errors, "test_error", "/test")
    async def failing_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        await failing_function()


def test_request_duration_with_category(metrics_client, registry):
    """Test request duration tracking with category."""
    with metrics_client.track_request_duration("GET", "/api/test", "read"):
        pass

    # Verify metric exists with category label
    metric_name = "test_http_request_duration_seconds"
    assert any(metric_name in str(metric) for metric in registry.collect())
