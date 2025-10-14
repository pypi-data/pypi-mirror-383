"""Cache manager for Redis-backed caching."""
from __future__ import annotations

import logging
from typing import Any, Callable, Iterable

import redis.asyncio as redis

from kubemind_common.cache.serializers import JSONSerializer, Serializer

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-backed cache manager with TTL support.

    Usage:
        cache = CacheManager(redis_client, prefix="myapp")

        # Set cache
        await cache.set("user:123", user_data, ttl=300)

        # Get cache
        user_data = await cache.get("user:123")

        # Delete cache
        await cache.delete("user:123")

        # Delete by pattern
        await cache.delete_pattern("user:*")
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        prefix: str = "cache",
        serializer: Serializer | None = None
    ):
        """Initialize cache manager.

        Args:
            redis_client: Redis async client
            prefix: Key prefix for namespacing (default: "cache")
            serializer: Serializer for values (default: JSONSerializer)
        """
        self.redis = redis_client
        self.prefix = prefix
        self.serializer = serializer or JSONSerializer()

    def _make_key(self, key: str) -> str:
        """Create namespaced cache key.

        Args:
            key: Original key

        Returns:
            Namespaced key with prefix
        """
        return f"{self.prefix}:{key}"

    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        try:
            data = await self.redis.get(self._make_key(key))
            if data is None:
                return default
            return self.serializer.deserialize(data)
        except Exception as e:
            logger.warning(f"Cache get error for key '{key}': {e}")
            return default

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = no expiration)

        Returns:
            True if successful
        """
        try:
            data = self.serializer.serialize(value)
            if ttl:
                await self.redis.setex(self._make_key(key), ttl, data)
            else:
                await self.redis.set(self._make_key(key), data)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted
        """
        try:
            result = await self.redis.delete(self._make_key(key))
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    async def delete_many(self, keys: Iterable[str]) -> int:
        """Delete multiple keys from cache.

        Args:
            keys: Iterable of cache keys

        Returns:
            Number of keys deleted
        """
        try:
            full_keys = [self._make_key(k) for k in keys]
            if not full_keys:
                return 0
            return await self.redis.delete(*full_keys)
        except Exception as e:
            logger.error(f"Cache delete_many error: {e}")
            return 0

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        try:
            full_pattern = self._make_key(pattern)
            cursor = 0
            deleted_count = 0

            while True:
                cursor, keys = await self.redis.scan(cursor, match=full_pattern, count=100)
                if keys:
                    deleted_count += await self.redis.delete(*keys)
                if cursor == 0:
                    break

            return deleted_count
        except Exception as e:
            logger.error(f"Cache delete_pattern error for pattern '{pattern}': {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        try:
            result = await self.redis.exists(self._make_key(key))
            return result > 0
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Get remaining TTL for key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        try:
            return await self.redis.ttl(self._make_key(key))
        except Exception as e:
            logger.error(f"Cache ttl error for key '{key}': {e}")
            return -2

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for key.

        Args:
            key: Cache key
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            result = await self.redis.expire(self._make_key(key), ttl)
            return result > 0
        except Exception as e:
            logger.error(f"Cache expire error for key '{key}': {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value in cache.

        Args:
            key: Cache key
            amount: Amount to increment (default: 1)

        Returns:
            New value after increment
        """
        try:
            return await self.redis.incrby(self._make_key(key), amount)
        except Exception as e:
            logger.error(f"Cache increment error for key '{key}': {e}")
            raise

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement numeric value in cache.

        Args:
            key: Cache key
            amount: Amount to decrement (default: 1)

        Returns:
            New value after decrement
        """
        try:
            return await self.redis.decrby(self._make_key(key), amount)
        except Exception as e:
            logger.error(f"Cache decrement error for key '{key}': {e}")
            raise

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: int | None = None
    ) -> Any:
        """Get value from cache or compute and set if missing.

        Args:
            key: Cache key
            factory: Callable that returns value if cache miss
            ttl: Time-to-live in seconds for new values

        Returns:
            Cached or computed value
        """
        value = await self.get(key)
        if value is not None:
            return value

        value = factory() if not callable(factory) or not hasattr(factory, '__await__') else await factory()
        await self.set(key, value, ttl)
        return value

    async def clear(self) -> int:
        """Clear all keys with this cache's prefix.

        Returns:
            Number of keys deleted
        """
        return await self.delete_pattern("*")
