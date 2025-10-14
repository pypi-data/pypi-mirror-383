"""Circuit breaker pattern for preventing cascading failures."""
from __future__ import annotations

import asyncio
import functools
import logging
import time
from enum import Enum
from typing import Any, Callable, Type

logger = logging.getLogger(__name__)


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, requests pass through
    OPEN = "open"  # Failing, reject requests immediately
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures.

    States:
        - CLOSED: Normal operation, requests allowed
        - OPEN: Service failing, requests rejected immediately
        - HALF_OPEN: Testing recovery, limited requests allowed

    Usage:
        cb = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=HTTPException
        )

        async def call_external_api():
            async with cb:
                return await external_api.request()
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
        half_open_max_calls: int = 1,
        name: str | None = None
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to count as failure
            half_open_max_calls: Max calls allowed in half-open state
            name: Circuit breaker name for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.half_open_max_calls = half_open_max_calls
        self.name = name or "circuit_breaker"

        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitBreakerState:
        """Get current state."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    async def __aenter__(self) -> CircuitBreaker:
        """Async context manager entry."""
        await self._call()
        return self

    async def __aexit__(self, exc_type: Type[Exception] | None, exc_val: Exception | None, exc_tb: Any) -> bool:
        """Async context manager exit."""
        if exc_type is None:
            # Success
            await self._on_success()
            return False

        if isinstance(exc_val, self.expected_exception):
            # Expected failure
            await self._on_failure()
            return False  # Re-raise exception

        # Unexpected exception, don't count as failure
        return False

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute function through circuit breaker.

        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
        """
        async with self:
            return await func(*args, **kwargs)

    async def _call(self) -> None:
        """Check if call is allowed."""
        async with self._lock:
            current_state = await self._get_state()

            if current_state == CircuitBreakerState.OPEN:
                logger.warning(f"Circuit breaker '{self.name}' is OPEN, rejecting call")
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service unavailable, please try again later."
                )

            if current_state == CircuitBreakerState.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    logger.warning(
                        f"Circuit breaker '{self.name}' HALF_OPEN call limit reached"
                    )
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' is HALF_OPEN. "
                        f"Too many concurrent test requests."
                    )
                self._half_open_calls += 1

    async def _get_state(self) -> CircuitBreakerState:
        """Get current state, transitioning to HALF_OPEN if recovery timeout elapsed."""
        if self._state == CircuitBreakerState.OPEN:
            if self._last_failure_time is not None:
                elapsed = time.time() - self._last_failure_time
                if elapsed >= self.recovery_timeout:
                    logger.info(
                        f"Circuit breaker '{self.name}' transitioning to HALF_OPEN "
                        f"after {elapsed:.1f}s"
                    )
                    self._state = CircuitBreakerState.HALF_OPEN
                    self._half_open_calls = 0

        return self._state

    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            if self._state == CircuitBreakerState.HALF_OPEN:
                logger.info(f"Circuit breaker '{self.name}' transitioning to CLOSED")
                self._state = CircuitBreakerState.CLOSED
                self._failure_count = 0
                self._half_open_calls = 0
            elif self._state == CircuitBreakerState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0

    async def _on_failure(self) -> None:
        """Handle failed call."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitBreakerState.HALF_OPEN:
                logger.warning(
                    f"Circuit breaker '{self.name}' failed in HALF_OPEN, "
                    f"transitioning to OPEN"
                )
                self._state = CircuitBreakerState.OPEN
                self._half_open_calls = 0

            elif self._state == CircuitBreakerState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    logger.warning(
                        f"Circuit breaker '{self.name}' threshold reached "
                        f"({self._failure_count}/{self.failure_threshold}), "
                        f"transitioning to OPEN"
                    )
                    self._state = CircuitBreakerState.OPEN

    async def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        async with self._lock:
            logger.info(f"Circuit breaker '{self.name}' manually reset to CLOSED")
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._half_open_calls = 0
            self._last_failure_time = None


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception,
    name: str | None = None
) -> Callable:
    """Decorator to wrap function with circuit breaker.

    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery
        expected_exception: Exception type to count as failure
        name: Circuit breaker name for logging

    Returns:
        Decorated function

    Usage:
        @circuit_breaker(failure_threshold=3, recovery_timeout=30)
        async def call_external_service():
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.example.com")
                return response.json()
    """
    cb = CircuitBreaker(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        expected_exception=expected_exception,
        name=name
    )

    def decorator(func: Callable) -> Callable:
        # Set circuit breaker name from function if not provided
        if name is None:
            cb.name = f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await cb.call(func, *args, **kwargs)

        # Attach circuit breaker instance to wrapper for inspection
        wrapper.circuit_breaker = cb  # type: ignore

        return wrapper

    return decorator
