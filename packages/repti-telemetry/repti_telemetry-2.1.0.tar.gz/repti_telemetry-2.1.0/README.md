# ReptiDex Telemetry

Unified observability library for ReptiDex microservices, providing logging, metrics, and tracing capabilities.

## Features

### Logging
- **Structured JSON logging** with full request context
- **PII filtering** for automatic redaction of sensitive data
- **Error fingerprinting** for grouping similar errors
- **Context tracking** across async boundaries (request_id, user_id, session_id, etc.)
- **FastAPI middleware** for automatic request logging
- **Decorators** for endpoint, error, and performance logging

### Metrics
- **Prometheus integration** with pre-configured metrics
- **FastAPI middleware** for automatic HTTP metrics collection
- **Business metrics** for ReptiDex-specific operations (vivariums, animals)
- **Database and cache metrics**

### Infrastructure
- **Loki** for log aggregation
- **Prometheus** for metrics collection
- **Grafana** for visualization
- **Fluent Bit** for log routing
- **AlertManager** for alerting

## Installation

```bash
# Basic installation (logging only)
pip install repti-telemetry

# With FastAPI support
pip install repti-telemetry[fastapi]

# With metrics support
pip install repti-telemetry[metrics]

# All features
pip install repti-telemetry[all]
```

## Quick Start

### Logging

```python
from repti_telemetry import setup_logging, get_logger, LogContext

# Initialize logging (call once at startup)
setup_logging(
    service_name="repti-core",
    log_level="INFO",
    enable_pii_filtering=True,
)

# Get a logger
logger = get_logger(__name__)

# Log with context
with LogContext(request_id="abc123", user_id="user456"):
    logger.info("Processing request", extra={"action": "fetch_vivarium"})
```

### FastAPI Logging Middleware

```python
from fastapi import FastAPI
from repti_telemetry.logging import RequestLoggingMiddleware

app = FastAPI()
app.add_middleware(RequestLoggingMiddleware)
```

### Decorators

```python
from repti_telemetry.logging import log_endpoint, log_errors, log_performance

@log_endpoint(log_args=True, log_duration=True)
@log_errors(log_traceback=True)
@log_performance(threshold_ms=500.0)
async def get_vivarium(vivarium_id: str):
    return await db.get_vivarium(vivarium_id)
```

### Metrics

```python
from repti_telemetry.metrics import MetricsClient, MetricsMiddleware
from repti_telemetry.metrics.middleware import setup_metrics_endpoint

# Create metrics client
metrics = MetricsClient(service_name="repti-core")

# Add middleware to FastAPI
app.add_middleware(MetricsMiddleware, metrics_client=metrics)

# Add /metrics endpoint
setup_metrics_endpoint(app)

# Use metrics in your code
metrics.increment_vivarium_operation("create", status="success")

with metrics.track_db_query_duration("select"):
    results = await db.query()
```

## Configuration

### Environment Variables

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FORMAT`: Log format (json, text)
- `SERVICE_NAME`: Name of the service
- `ENABLE_PII_FILTERING`: Enable PII redaction (true/false)

### Context Variables

The following context variables are automatically included in logs:

- `request_id`: Unique request identifier
- `correlation_id`: Cross-service correlation ID
- `user_id`: Authenticated user ID
- `session_id`: Session identifier
- `endpoint`: API endpoint path
- `method`: HTTP method
- `vivarium_id`: Vivarium ID (ReptiDex-specific)
- `animal_id`: Animal ID (ReptiDex-specific)
- `transaction_id`: Transaction ID (ReptiDex-specific)

## Infrastructure

### Deploying Monitoring Stack

The monitoring infrastructure is included in `infrastructure/`:

```bash
# Build and push monitoring images
cd backend/shared/repti-telemetry
./infrastructure/build-and-push.sh dev

# Deploy via CloudFormation
aws cloudformation deploy \
  --template-file infrastructure/templates/07-monitoring.yaml \
  --stack-name dev-reptidex-monitoring \
  --capabilities CAPABILITY_IAM
```

### Grafana Dashboards

Pre-configured dashboards are included:
- **Services Overview**: High-level service health and performance
- **Logs Explorer**: Log search and analysis
- **Error Tracking**: Error rates and grouping by fingerprint
- **Performance Analysis**: Request latency and throughput
- **Performance SLA**: SLA compliance tracking

### Prometheus Metrics

Exposed at `/metrics` endpoint:
- `reptidex_http_requests_total`: Total HTTP requests
- `reptidex_http_request_duration_seconds`: Request duration histogram
- `reptidex_http_requests_in_progress`: Requests currently processing
- `reptidex_db_query_duration_seconds`: Database query duration
- `reptidex_cache_hits_total`: Cache hits
- `reptidex_vivarium_operations_total`: Vivarium operations
- `reptidex_animal_operations_total`: Animal operations
- `reptidex_errors_total`: Errors by type

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black repti_telemetry/
isort repti_telemetry/

# Type checking
mypy repti_telemetry/

# Linting
flake8 repti_telemetry/
```

## Migration from repti-logging

If you're migrating from the old `repti-logging` package:

1. Update imports:
   ```python
   # Old
   from repti_logging import setup_logging, get_logger

   # New
   from repti_telemetry import setup_logging, get_logger
   ```

2. Update dependencies in `requirements.txt`:
   ```
   # Old
   repti-logging>=1.0.0

   # New
   repti-telemetry>=2.0.0
   ```

3. The API is backward compatible - all existing logging functionality works the same way.

## Architecture

```
repti_telemetry/
├── logging/              # Structured logging with PII filtering
│   ├── setup.py         # Logger configuration
│   ├── formatter.py     # JSON formatter with error fingerprinting
│   ├── middleware.py    # FastAPI request logging
│   ├── context.py       # Context variables for tracking
│   ├── decorators.py    # Logging decorators
│   └── filters.py       # PII filtering
├── metrics/             # Prometheus metrics
│   ├── client.py        # Metrics client
│   └── middleware.py    # FastAPI metrics middleware
├── tracing/             # Distributed tracing (future)
└── healthcheck/         # Health check utilities (future)

infrastructure/
├── loki/                # Log aggregation
├── prometheus/          # Metrics collection
├── grafana/             # Visualization
├── fluent-bit/          # Log routing
├── alertmanager/        # Alerting
└── alerts/              # Alert rules
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please contact the ReptiDex development team.
