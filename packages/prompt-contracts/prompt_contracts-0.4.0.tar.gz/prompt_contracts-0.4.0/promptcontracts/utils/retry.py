"""Retry utilities with exponential backoff."""

import functools
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        exceptions: Tuple of exception types to catch and retry

    Example:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        def unstable_api_call():
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # Last attempt failed, re-raise
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base**attempt), max_delay)
                    time.sleep(delay)

            # Should never reach here, but for type safety
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def retry_on_timeout(max_retries: int = 2, base_delay: float = 2.0):
    """
    Specialized retry decorator for timeout errors.

    Retries on common timeout exceptions from requests/httpx.
    """
    import httpx

    timeout_exceptions = (
        TimeoutError,
        httpx.TimeoutException,
    )

    return retry_with_backoff(
        max_retries=max_retries, base_delay=base_delay, exceptions=timeout_exceptions
    )
