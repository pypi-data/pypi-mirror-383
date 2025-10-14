from __future__ import annotations

import asyncio


class DummyPipe:
    def __init__(self, store):
        self.store = store
        self.ops = []

    def get(self, key):
        self.ops.append(("get", key))
        return self

    def set(self, key, value, ex=None):
        self.ops.append(("set", key, value, ex))
        return self

    async def execute(self):
        results = []
        for op in self.ops:
            if op[0] == "get":
                results.append(self.store.get(op[1]))
            elif op[0] == "set":
                _, key, val, _ = op
                self.store[key] = val
        self.ops.clear()
        return results


class DummyRedis:
    def __init__(self):
        self.store = {}

    def pipeline(self):
        return DummyPipe(self.store)


def test_token_bucket_limiter_monkeypatch(monkeypatch):
    from kubemind_common.middleware.rate_limit import TokenBucketLimiter

    dummy = DummyRedis()

    # monkeypatch the factory function to return our dummy synchronously
    monkeypatch.setattr(
        "kubemind_common.middleware.rate_limit.get_async_redis", lambda url: dummy
    )

    limiter = TokenBucketLimiter(
        key_prefix="t", capacity=1, refill_rate_per_sec=0, redis_url="redis://test"
    )

    async def flow():
        ok1 = await limiter.allow("client")
        ok2 = await limiter.allow("client")
        return ok1, ok2

    ok1, ok2 = asyncio.get_event_loop().run_until_complete(flow())
    assert ok1 is True
    assert ok2 is False

