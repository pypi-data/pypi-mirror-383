"""Retry utilities with exponential backoff and jitter."""
from __future__ import annotations

import asyncio
import functools
import logging
import random
from typing import Any, Callable, Type

from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random_exponential,
)

logger = logging.getLogger(__name__)


class RetryConfig:
    """Retry configuration presets."""

    @staticmethod
    def network() -> dict[str, Any]:
        """Configuration for network/HTTP requests.

        Returns:
            Tenacity retry config for network calls
        """
        return {
            "stop": stop_after_attempt(3),
            "wait": wait_exponential(multiplier=1, min=1, max=10),
            "retry": retry_if_exception_type((ConnectionError, TimeoutError)),
            "reraise": True,
        }

    @staticmethod
    def database() -> dict[str, Any]:
        """Configuration for database operations.

        Returns:
            Tenacity retry config for database calls
        """
        return {
            "stop": stop_after_attempt(5),
            "wait": wait_exponential(multiplier=0.5, min=0.5, max=5),
            "reraise": True,
        }

    @staticmethod
    def external_api() -> dict[str, Any]:
        """Configuration for external API calls.

        Returns:
            Tenacity retry config for external API calls
        """
        return {
            "stop": stop_after_attempt(4),
            "wait": wait_random_exponential(multiplier=1, max=20),
            "reraise": True,
        }

    @staticmethod
    def fast() -> dict[str, Any]:
        """Configuration for fast operations.

        Returns:
            Tenacity retry config for fast operations
        """
        return {
            "stop": stop_after_attempt(3),
            "wait": wait_exponential(multiplier=0.1, min=0.1, max=1),
            "reraise": True,
        }


def retry_with_backoff(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_on: Type[Exception] | tuple[Type[Exception], ...] = Exception,
    logger_name: str | None = None
) -> Callable:
    """Decorator for retry with exponential backoff and optional jitter.

    Args:
        max_attempts: Maximum number of attempts
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to prevent thundering herd
        retry_on: Exception type(s) to retry on
        logger_name: Logger name for logging retry attempts

    Returns:
        Decorated function

    Usage:
        @retry_with_backoff(max_attempts=5, min_wait=1, max_wait=30)
        async def fetch_data():
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.example.com")
                response.raise_for_status()
                return response.json()
    """
    def decorator(func: Callable) -> Callable:
        log = logging.getLogger(logger_name or func.__module__)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            last_exception = None

            while attempt < max_attempts:
                attempt += 1
                try:
                    result = await func(*args, **kwargs)
                    if attempt > 1:
                        log.info(
                            f"{func.__qualname__} succeeded on attempt {attempt}/{max_attempts}"
                        )
                    return result
                except retry_on as e:
                    last_exception = e
                    if attempt >= max_attempts:
                        log.error(
                            f"{func.__qualname__} failed after {attempt} attempts: {e}"
                        )
                        raise

                    # Calculate wait time with exponential backoff
                    wait_time = min(min_wait * (exponential_base ** (attempt - 1)), max_wait)

                    # Add jitter to prevent thundering herd
                    if jitter:
                        wait_time = wait_time * (0.5 + random.random() * 0.5)

                    log.warning(
                        f"{func.__qualname__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {wait_time:.2f}s..."
                    )
                    await asyncio.sleep(wait_time)

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"Unexpected retry loop exit for {func.__qualname__}")

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            raise RuntimeError(
                f"Cannot use @retry_with_backoff decorator on sync function {func.__name__}. "
                f"Use async functions only."
            )

        # Determine if function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def retry_with_tenacity(
    config: dict[str, Any] | None = None,
    preset: str | None = None
) -> Callable:
    """Decorator for retry using tenacity library directly.

    Args:
        config: Tenacity configuration dict
        preset: Preset name from RetryConfig ('network', 'database', 'external_api', 'fast')

    Returns:
        Decorated function

    Usage:
        # Using preset
        @retry_with_tenacity(preset="network")
        async def fetch_data():
            ...

        # Using custom config
        @retry_with_tenacity(config={
            "stop": stop_after_attempt(5),
            "wait": wait_exponential(max=30)
        })
        async def process_data():
            ...
    """
    if preset:
        config = getattr(RetryConfig, preset)()
    elif config is None:
        config = RetryConfig.network()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            async for attempt in AsyncRetrying(**config):
                with attempt:
                    return await func(*args, **kwargs)

        return wrapper

    return decorator
