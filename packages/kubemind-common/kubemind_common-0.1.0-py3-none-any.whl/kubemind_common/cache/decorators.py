"""Cache decorators for function memoization."""
from __future__ import annotations

import functools
import hashlib
import inspect
import logging
from typing import Any, Callable

from kubemind_common.cache.manager import CacheManager

logger = logging.getLogger(__name__)


def _make_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    """Generate cache key from function and arguments.

    Args:
        func: Function being cached
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    # Get function module and name
    module = func.__module__
    qualname = func.__qualname__

    # Create args signature
    arg_parts = [repr(arg) for arg in args]
    kwarg_parts = [f"{k}={repr(v)}" for k, v in sorted(kwargs.items())]
    all_parts = arg_parts + kwarg_parts
    args_str = ",".join(all_parts)

    # Hash if too long
    if len(args_str) > 200:
        args_hash = hashlib.md5(args_str.encode()).hexdigest()
        return f"func:{module}.{qualname}:{args_hash}"

    return f"func:{module}.{qualname}:{args_str}"


def cached(
    cache_manager: CacheManager,
    ttl: int | None = 300,
    key_prefix: str | None = None,
    key_builder: Callable[[Callable, tuple, dict], str] | None = None
) -> Callable:
    """Decorator to cache function results.

    Args:
        cache_manager: CacheManager instance
        ttl: Time-to-live in seconds (None = no expiration)
        key_prefix: Optional prefix for cache keys
        key_builder: Optional custom key builder function

    Returns:
        Decorated function

    Usage:
        from kubemind_common.cache import CacheManager, cached

        cache = CacheManager(redis_client)

        @cached(cache, ttl=60)
        async def get_user(user_id: str):
            # Expensive database query
            return await db.query(User).get(user_id)

        # First call - cache miss, executes function
        user = await get_user("123")

        # Second call - cache hit, returns cached value
        user = await get_user("123")
    """
    def decorator(func: Callable) -> Callable:
        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Build cache key
            if key_builder:
                cache_key = key_builder(func, args, kwargs)
            else:
                cache_key = _make_cache_key(func, args, kwargs)

            if key_prefix:
                cache_key = f"{key_prefix}:{cache_key}"

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value

            # Cache miss - execute function
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_manager.set(cache_key, result, ttl)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            raise RuntimeError(f"Cannot use @cached decorator on sync function {func.__name__}. Use async functions only.")

        return async_wrapper if is_async else sync_wrapper

    return decorator


def cached_method(
    cache_manager_attr: str = "cache",
    ttl: int | None = 300,
    key_prefix: str | None = None
) -> Callable:
    """Decorator to cache class method results.

    The class must have a cache_manager attribute.

    Args:
        cache_manager_attr: Name of cache manager attribute on class (default: "cache")
        ttl: Time-to-live in seconds (None = no expiration)
        key_prefix: Optional prefix for cache keys

    Returns:
        Decorated method

    Usage:
        class UserService:
            def __init__(self, cache: CacheManager):
                self.cache = cache

            @cached_method(cache_manager_attr="cache", ttl=60)
            async def get_user(self, user_id: str):
                return await db.query(User).get(user_id)
    """
    def decorator(func: Callable) -> Callable:
        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            # Get cache manager from instance
            if not hasattr(self, cache_manager_attr):
                raise AttributeError(
                    f"Class {self.__class__.__name__} missing '{cache_manager_attr}' attribute"
                )

            cache_manager: CacheManager = getattr(self, cache_manager_attr)

            # Build cache key (include class name)
            class_name = self.__class__.__name__
            cache_key = _make_cache_key(func, args, kwargs)
            cache_key = f"{class_name}.{cache_key}"

            if key_prefix:
                cache_key = f"{key_prefix}:{cache_key}"

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value

            # Cache miss - execute method
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(self, *args, **kwargs)

            # Store in cache
            await cache_manager.set(cache_key, result, ttl)
            return result

        @functools.wraps(func)
        def sync_wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            raise RuntimeError(f"Cannot use @cached_method decorator on sync method {func.__name__}. Use async methods only.")

        return async_wrapper if is_async else sync_wrapper

    return decorator


def invalidate_cache(
    cache_manager: CacheManager,
    key_pattern: str
) -> Callable:
    """Decorator to invalidate cache after function execution.

    Args:
        cache_manager: CacheManager instance
        key_pattern: Pattern for keys to invalidate (e.g., "user:*")

    Returns:
        Decorated function

    Usage:
        @invalidate_cache(cache, "user:*")
        async def update_user(user_id: str, data: dict):
            await db.update(User, user_id, data)
    """
    def decorator(func: Callable) -> Callable:
        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = await func(*args, **kwargs)
            # Invalidate cache after successful execution
            await cache_manager.delete_pattern(key_pattern)
            logger.debug(f"Invalidated cache pattern: {key_pattern}")
            return result

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            raise RuntimeError(f"Cannot use @invalidate_cache decorator on sync function {func.__name__}. Use async functions only.")

        return async_wrapper if is_async else sync_wrapper

    return decorator
