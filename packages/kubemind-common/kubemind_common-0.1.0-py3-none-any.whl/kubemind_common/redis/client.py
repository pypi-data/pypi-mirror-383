from __future__ import annotations

import redis.asyncio as redis


def get_async_redis(url: str) -> redis.Redis:
    return redis.from_url(url, encoding="utf-8", decode_responses=True)

