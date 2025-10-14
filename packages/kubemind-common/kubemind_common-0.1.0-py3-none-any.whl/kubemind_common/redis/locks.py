from __future__ import annotations

import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class LockAcquisitionError(Exception):
    """Raised when lock cannot be acquired."""

    pass


class LockTimeout(Exception):
    """Raised when lock acquisition times out."""

    pass


@asynccontextmanager
async def redis_lock(
    client: redis.Redis,
    key: str,
    ttl: int = 30,
    retry: bool = False,
    retry_timeout: float = 10.0,
    retry_interval: float = 0.1
):
    """Distributed lock using Redis with optional retry.

    Args:
        client: Redis async client
        key: Lock key
        ttl: Lock TTL in seconds
        retry: Whether to retry acquiring lock
        retry_timeout: Max time to wait for lock (seconds)
        retry_interval: Interval between retry attempts (seconds)

    Raises:
        LockAcquisitionError: If lock cannot be acquired immediately and retry=False
        LockTimeout: If lock cannot be acquired within retry_timeout

    Usage:
        # Simple lock (fail immediately if not available)
        async with redis_lock(redis_client, "mylock"):
            # Critical section
            ...

        # Lock with retry
        async with redis_lock(redis_client, "mylock", retry=True, retry_timeout=5):
            # Critical section
            ...
    """
    token = str(uuid.uuid4())
    lock_key = f"lock:{key}"
    acquired = False
    start_time = time.time()

    # Try to acquire lock with optional retry
    while not acquired:
        acquired = await client.set(lock_key, token, ex=ttl, nx=True)

        if acquired:
            logger.debug(f"Lock acquired: {key}")
            break

        if not retry:
            logger.warning(f"Lock not acquired: {key}")
            raise LockAcquisitionError(f"Failed to acquire lock: {key}")

        # Check timeout
        elapsed = time.time() - start_time
        if elapsed >= retry_timeout:
            logger.error(f"Lock acquisition timeout after {elapsed:.2f}s: {key}")
            raise LockTimeout(f"Failed to acquire lock within {retry_timeout}s: {key}")

        # Wait before retry
        logger.debug(f"Lock busy, retrying in {retry_interval}s: {key}")
        await asyncio.sleep(retry_interval)

    try:
        yield
    finally:
        # Best-effort release with token verification
        try:
            cur = await client.get(lock_key)
            if cur == token:
                await client.delete(lock_key)
                logger.debug(f"Lock released: {key}")
            else:
                logger.warning(f"Lock token mismatch, not releasing: {key}")
        except Exception as e:
            logger.error(f"Error releasing lock {key}: {e}")


class RedisLock:
    """Reentrant Redis lock with automatic renewal.

    Usage:
        lock = RedisLock(redis_client, "mylock", ttl=30)

        async with lock:
            # Critical section
            # Lock is automatically renewed if operation takes longer than TTL
            ...

        # Or use manually:
        await lock.acquire()
        try:
            # Critical section
            ...
        finally:
            await lock.release()
    """

    def __init__(
        self,
        client: redis.Redis,
        key: str,
        ttl: int = 30,
        auto_renewal: bool = True,
        renewal_interval: float | None = None
    ):
        """Initialize Redis lock.

        Args:
            client: Redis async client
            key: Lock key
            ttl: Lock TTL in seconds
            auto_renewal: Enable automatic lock renewal
            renewal_interval: Interval for auto-renewal (default: ttl/3)
        """
        self.client = client
        self.key = key
        self.lock_key = f"lock:{key}"
        self.ttl = ttl
        self.auto_renewal = auto_renewal
        self.renewal_interval = renewal_interval or (ttl / 3)
        self.token: str | None = None
        self._renewal_task: asyncio.Task | None = None

    async def acquire(self, timeout: float | None = None) -> bool:
        """Acquire lock with optional timeout.

        Args:
            timeout: Max time to wait for lock (None = wait forever)

        Returns:
            True if acquired

        Raises:
            LockTimeout: If timeout expires
        """
        self.token = str(uuid.uuid4())
        start_time = time.time()

        while True:
            acquired = await self.client.set(self.lock_key, self.token, ex=self.ttl, nx=True)

            if acquired:
                logger.debug(f"Lock acquired: {self.key}")

                # Start auto-renewal if enabled
                if self.auto_renewal:
                    self._renewal_task = asyncio.create_task(self._auto_renew())

                return True

            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    raise LockTimeout(f"Failed to acquire lock within {timeout}s: {self.key}")

            await asyncio.sleep(0.1)

    async def release(self) -> bool:
        """Release lock.

        Returns:
            True if released successfully
        """
        # Cancel auto-renewal
        if self._renewal_task:
            self._renewal_task.cancel()
            try:
                await self._renewal_task
            except asyncio.CancelledError:
                pass
            self._renewal_task = None

        # Release lock with token verification
        if not self.token:
            return False

        try:
            cur = await self.client.get(self.lock_key)
            if cur == self.token:
                await self.client.delete(self.lock_key)
                logger.debug(f"Lock released: {self.key}")
                return True
            else:
                logger.warning(f"Lock token mismatch: {self.key}")
                return False
        except Exception as e:
            logger.error(f"Error releasing lock {self.key}: {e}")
            return False
        finally:
            self.token = None

    async def _auto_renew(self) -> None:
        """Background task to automatically renew lock."""
        while True:
            try:
                await asyncio.sleep(self.renewal_interval)

                if not self.token:
                    break

                # Renew lock
                result = await self.client.expire(self.lock_key, self.ttl)
                if result:
                    logger.debug(f"Lock renewed: {self.key}")
                else:
                    logger.warning(f"Failed to renew lock: {self.key}")
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in lock auto-renewal for {self.key}: {e}")
                break

    async def __aenter__(self) -> RedisLock:
        """Async context manager entry."""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.release()

