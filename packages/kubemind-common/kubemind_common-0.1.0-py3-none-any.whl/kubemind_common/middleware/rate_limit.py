from __future__ import annotations

import time
from typing import Callable

from fastapi import HTTPException, Request

from kubemind_common.redis.client import get_async_redis


class TokenBucketLimiter:
    def __init__(self, key_prefix: str, capacity: int, refill_rate_per_sec: float, redis_url: str):
        self.key = f"ratelimit:{key_prefix}"
        self.capacity = capacity
        self.refill = refill_rate_per_sec
        self.redis_url = redis_url

    async def allow(self, token: str) -> bool:
        r = get_async_redis(self.redis_url)
        now = int(time.time())
        pipe = r.pipeline()
        # tokens key and timestamp key
        tokens_key = f"{self.key}:{token}:tokens"
        ts_key = f"{self.key}:{token}:ts"
        # get last state
        pipe.get(tokens_key)
        pipe.get(ts_key)
        cur_tokens, last_ts = await pipe.execute()
        cur_tokens = float(cur_tokens) if cur_tokens is not None else float(self.capacity)
        last_ts = int(last_ts) if last_ts is not None else now
        # refill
        elapsed = max(0, now - last_ts)
        cur_tokens = min(self.capacity, cur_tokens + elapsed * self.refill)
        if cur_tokens < 1:
            # store updated state
            pipe.set(tokens_key, cur_tokens, ex=60)
            pipe.set(ts_key, now, ex=60)
            await pipe.execute()
            return False
        # consume 1 token
        cur_tokens -= 1
        pipe.set(tokens_key, cur_tokens, ex=60)
        pipe.set(ts_key, now, ex=60)
        await pipe.execute()
        return True


def rate_limit_middleware(limiter: TokenBucketLimiter):
    async def _mw(request: Request, call_next: Callable):
        token = request.client.host if request.client else "anonymous"
        ok = await limiter.allow(token)
        if not ok:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        return await call_next(request)

    return _mw

