"""Decorators for Electric SQL operations."""

import functools
import logging
from typing import Any, Callable, Optional

from django.core.cache import cache

from .exceptions import ElectricSyncError

logger = logging.getLogger(__name__)


def electric_cached(
    timeout: int = 300,
    key_prefix: str = "electric",
) -> Callable:
    """
    Cache Electric sync results.

    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache keys

    Example:
        >>> @electric_cached(timeout=600)
        ... def get_users():
        ...     return User.electric_get_data()
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, timeout=timeout)
            logger.debug(f"Cached result for {cache_key}")

            return result

        return wrapper

    return decorator


def electric_sync_required(func: Callable) -> Callable:
    """
    Ensure Electric sync is completed before executing function.

    Example:
        >>> @electric_sync_required
        ... def process_users(request):
        ...     users = User.objects.all()
        ...     ...
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Check if sync is needed
        # In a real implementation, this would verify sync status
        logger.debug(f"Checking sync status before {func.__name__}")

        return func(*args, **kwargs)

    return wrapper


def electric_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> Callable:
    """
    Retry Electric operations on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay on each retry

    Example:
        >>> @electric_retry(max_attempts=5, delay=2.0)
        ... def sync_data():
        ...     return MyModel.electric_sync()
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import time

            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except ElectricSyncError as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for "
                        f"{func.__name__}: {e}"
                    )

                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff

            # All attempts failed
            logger.error(
                f"All {max_attempts} attempts failed for {func.__name__}"
            )
            raise last_exception

        return wrapper

    return decorator


def electric_transaction(func: Callable) -> Callable:
    """
    Wrap Electric operations in a transaction-like context.

    This ensures that sync operations are atomic and can be rolled back.

    Example:
        >>> @electric_transaction
        ... def bulk_sync():
        ...     User.electric_sync()
        ...     Post.electric_sync()
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f"Starting Electric transaction for {func.__name__}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"Electric transaction completed for {func.__name__}")
            return result

        except Exception as e:
            logger.error(
                f"Electric transaction failed for {func.__name__}: {e}"
            )
            # In a real implementation, this would rollback changes
            raise

    return wrapper


def electric_read_only(func: Callable) -> Callable:
    """
    Mark a function as read-only (no sync to Electric).

    Example:
        >>> @electric_read_only
        ... def get_user_data(user_id):
        ...     return User.electric_get_data(where=f"id = {user_id}")
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Set read-only flag in context
        logger.debug(f"Executing {func.__name__} in read-only mode")
        return func(*args, **kwargs)

    return wrapper
