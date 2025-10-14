"""
Decorators for automatic logging of functions and endpoints.
"""

import functools
import time
from typing import Any, Callable, Optional

from repti_telemetry.logging.setup import get_logger

logger = get_logger(__name__)


def log_endpoint(
    log_args: bool = False,
    log_result: bool = False,
    log_duration: bool = True,
    logger_name: Optional[str] = None,
):
    """
    Decorator that automatically logs function entry, exit, and duration.

    Useful for logging API endpoints and service methods.

    Args:
        log_args: Log function arguments (use with caution for sensitive data)
        log_result: Log function return value (use with caution for sensitive data)
        log_duration: Log execution duration
        logger_name: Custom logger name (default: use function's module)

    Example:
        @log_endpoint(log_args=True, log_duration=True)
        async def get_user(user_id: str):
            return await db.get_user(user_id)
    """

    def decorator(func: Callable) -> Callable:
        func_logger = get_logger(logger_name or func.__module__)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = func.__name__
            log_extra = {"function": func_name}

            # Log arguments if enabled
            if log_args:
                log_extra["args"] = str(args) if args else None
                log_extra["kwargs"] = kwargs if kwargs else None

            func_logger.info(f"Entering {func_name}", extra=log_extra)
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Calculate duration
                if log_duration:
                    duration_ms = (time.time() - start_time) * 1000
                    log_extra["duration_ms"] = round(duration_ms, 2)

                # Log result if enabled
                if log_result:
                    log_extra["result"] = str(result)[:200]  # Limit size

                func_logger.info(f"Exiting {func_name}", extra=log_extra)
                return result

            except Exception as exc:
                duration_ms = (time.time() - start_time) * 1000
                func_logger.error(
                    f"Error in {func_name}",
                    extra={
                        "function": func_name,
                        "duration_ms": round(duration_ms, 2),
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                    },
                    exc_info=True,
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = func.__name__
            log_extra = {"function": func_name}

            # Log arguments if enabled
            if log_args:
                log_extra["args"] = str(args) if args else None
                log_extra["kwargs"] = kwargs if kwargs else None

            func_logger.info(f"Entering {func_name}", extra=log_extra)
            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                # Calculate duration
                if log_duration:
                    duration_ms = (time.time() - start_time) * 1000
                    log_extra["duration_ms"] = round(duration_ms, 2)

                # Log result if enabled
                if log_result:
                    log_extra["result"] = str(result)[:200]  # Limit size

                func_logger.info(f"Exiting {func_name}", extra=log_extra)
                return result

            except Exception as exc:
                duration_ms = (time.time() - start_time) * 1000
                func_logger.error(
                    f"Error in {func_name}",
                    extra={
                        "function": func_name,
                        "duration_ms": round(duration_ms, 2),
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                    },
                    exc_info=True,
                )
                raise

        # Return appropriate wrapper based on whether function is async
        if functools.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_errors(
    log_traceback: bool = True,
    reraise: bool = True,
    logger_name: Optional[str] = None,
):
    """
    Decorator that automatically logs exceptions with full context.

    Args:
        log_traceback: Include full stack trace in logs
        reraise: Re-raise the exception after logging (True) or suppress it (False)
        logger_name: Custom logger name (default: use function's module)

    Example:
        @log_errors(log_traceback=True, reraise=True)
        async def risky_operation():
            result = 1 / 0  # Will be logged with full context
    """

    def decorator(func: Callable) -> Callable:
        func_logger = get_logger(logger_name or func.__module__)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                func_logger.error(
                    f"Exception in {func.__name__}: {str(exc)}",
                    extra={
                        "function": func.__name__,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    },
                    exc_info=log_traceback,
                )
                if reraise:
                    raise
                return None

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                func_logger.error(
                    f"Exception in {func.__name__}: {str(exc)}",
                    extra={
                        "function": func.__name__,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    },
                    exc_info=log_traceback,
                )
                if reraise:
                    raise
                return None

        # Return appropriate wrapper based on whether function is async
        if functools.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_performance(
    threshold_ms: float = 1000.0,
    logger_name: Optional[str] = None,
):
    """
    Decorator that logs slow operations exceeding a duration threshold.

    Useful for identifying performance bottlenecks.

    Args:
        threshold_ms: Log warning if execution exceeds this threshold (milliseconds)
        logger_name: Custom logger name (default: use function's module)

    Example:
        @log_performance(threshold_ms=500.0)
        async def slow_database_query():
            # Will log warning if takes longer than 500ms
            return await db.query()
    """

    def decorator(func: Callable) -> Callable:
        func_logger = get_logger(logger_name or func.__module__)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            result = await func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000

            if duration_ms > threshold_ms:
                func_logger.warning(
                    f"Slow operation: {func.__name__}",
                    extra={
                        "function": func.__name__,
                        "duration_ms": round(duration_ms, 2),
                        "threshold_ms": threshold_ms,
                    },
                )

            return result

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000

            if duration_ms > threshold_ms:
                func_logger.warning(
                    f"Slow operation: {func.__name__}",
                    extra={
                        "function": func.__name__,
                        "duration_ms": round(duration_ms, 2),
                        "threshold_ms": threshold_ms,
                    },
                )

            return result

        # Return appropriate wrapper based on whether function is async
        if functools.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
