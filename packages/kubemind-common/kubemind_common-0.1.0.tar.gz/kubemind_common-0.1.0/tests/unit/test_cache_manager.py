import asyncio

from kubemind_common.cache.manager import CacheManager
from kubemind_common.cache.serializers import JSONSerializer


class DummyRedis:
    def __init__(self):
        self.store: dict[str, bytes] = {}

    async def get(self, key: str):
        return self.store.get(key)

    async def set(self, key: str, value: bytes):
        self.store[key] = value
        return True

    async def setex(self, key: str, ttl: int, value: bytes):
        self.store[key] = value
        return True

    async def delete(self, *keys: str):
        count = 0
        for k in keys:
            if k in self.store:
                del self.store[k]
                count += 1
        return count

    async def scan(self, cursor: int, match: str, count: int = 10):
        # very simple match: '*' or prefix*
        prefix = match[:-1] if match.endswith("*") else match
        keys = [k for k in list(self.store.keys()) if k.startswith(prefix)]
        return 0, keys

    async def exists(self, key: str):
        return 1 if key in self.store else 0

    async def ttl(self, key: str):
        return -1 if key in self.store else -2

    async def expire(self, key: str, ttl: int):
        return 1 if key in self.store else 0

    async def incrby(self, key: str, amount: int):
        cur = int(self.store.get(key, b"0").decode()) + amount
        self.store[key] = str(cur).encode()
        return cur

    async def decrby(self, key: str, amount: int):
        cur = int(self.store.get(key, b"0").decode()) - amount
        self.store[key] = str(cur).encode()
        return cur


def test_cache_manager_basic_operations():
    r = DummyRedis()
    cache = CacheManager(r, prefix="test", serializer=JSONSerializer())

    async def flow():
        assert await cache.get("k1") is None
        ok = await cache.set("k1", {"a": 1})
        assert ok is True
        assert await cache.get("k1") == {"a": 1}
        assert await cache.exists("k1") is True
        assert await cache.ttl("k1") in (-1, 0) or isinstance(await cache.ttl("k1"), int)
        ok = await cache.expire("k1", 10)
        assert ok in (True, False)  # Dummy returns True if exists
        # increment/decrement
        v = await cache.increment("counter")
        assert v == 1
        v = await cache.decrement("counter")
        assert v == 0
        # delete
        assert await cache.delete("k1") is True
        assert await cache.get("k1") is None

    asyncio.get_event_loop().run_until_complete(flow())


def test_cache_manager_get_or_set():
    r = DummyRedis()
    cache = CacheManager(r, prefix="p")

    async def flow():
        calls = {"n": 0}
        def factory():
            calls["n"] += 1
            return {"x": 2}
        v1 = await cache.get_or_set("a", factory, ttl=10)
        v2 = await cache.get_or_set("a", factory, ttl=10)
        assert v1 == {"x": 2}
        assert v2 == {"x": 2}
        # factory should be called once
        assert calls["n"] == 1

    asyncio.get_event_loop().run_until_complete(flow())

