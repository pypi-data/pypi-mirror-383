"""
Decorator utilities for easy metrics instrumentation.

This module provides decorators for tracking metrics on functions and methods,
supporting both synchronous and asynchronous functions.
"""

import functools
import time
from typing import Any, Callable, Optional

from prometheus_client import Counter, Gauge, Histogram


def track_duration(
    metric: Histogram,
    labels: Optional[dict] = None,
) -> Callable:
    """Tracks function execution time.

    Example:
        @track_duration(database_query_duration_seconds, {"query_type": "select"})
        async def get_user(user_id: str):
            ...

    Args:
        metric: Prometheus Histogram metric to track duration
        labels: Dictionary of label values for the metric

    Returns:
        Decorated function that tracks execution time
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

        # Return appropriate wrapper based on function type
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def track_count(
    metric: Counter,
    labels: Optional[dict] = None,
    increment: int = 1,
) -> Callable:
    """Tracks function execution count.

    Example:
        @track_count(users_registered_total)
        async def create_user(user_data: dict):
            ...

    Args:
        metric: Prometheus Counter metric to increment
        labels: Dictionary of label values for the metric
        increment: Amount to increment the counter (default: 1)

    Returns:
        Decorated function that increments counter on execution
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            result = await func(*args, **kwargs)
            if labels:
                metric.labels(**labels).inc(increment)
            else:
                metric.inc(increment)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            if labels:
                metric.labels(**labels).inc(increment)
            else:
                metric.inc(increment)
            return result

        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def track_in_progress(
    metric: Gauge,
    labels: Optional[dict] = None,
) -> Callable:
    """Tracks in-progress function executions.

    Example:
        @track_in_progress(http_requests_in_progress, {"method": "POST", "endpoint": "/users"})
        async def create_user(user_data: dict):
            ...

    Args:
        metric: Prometheus Gauge metric to track in-progress operations
        labels: Dictionary of label values for the metric

    Returns:
        Decorated function that tracks in-progress executions
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            if labels:
                metric.labels(**labels).inc()
            else:
                metric.inc()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                if labels:
                    metric.labels(**labels).dec()
                else:
                    metric.dec()

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            if labels:
                metric.labels(**labels).inc()
            else:
                metric.inc()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                if labels:
                    metric.labels(**labels).dec()
                else:
                    metric.dec()

        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def track_errors(  # noqa: C901
    metric: Counter,
    error_type: str,
    endpoint: Optional[str] = None,
) -> Callable:
    """Tracks errors in function execution.

    Example:
        @track_errors(errors_total, "database_error", "/users")
        async def get_user(user_id: str):
            ...

    Args:
        metric: Prometheus Counter metric to track errors
        error_type: Type/category of error
        endpoint: Optional endpoint name for context

    Returns:
        Decorated function that tracks errors
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                labels = {"error_type": error_type}
                if endpoint:
                    labels["endpoint"] = endpoint
                else:
                    labels["endpoint"] = func.__name__
                metric.labels(**labels).inc()
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                labels = {"error_type": error_type}
                if endpoint:
                    labels["endpoint"] = endpoint
                else:
                    labels["endpoint"] = func.__name__
                metric.labels(**labels).inc()
                raise

        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
