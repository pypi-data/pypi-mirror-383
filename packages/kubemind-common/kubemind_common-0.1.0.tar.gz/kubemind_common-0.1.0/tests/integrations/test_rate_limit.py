from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from kubemind_common.middleware.rate_limit import TokenBucketLimiter, rate_limit_middleware


class FakePipeline:
    def __init__(self, storage: dict[str, float]) -> None:
        self.storage = storage
        self.commands: list[tuple[str, str, float | None]] = []

    def get(self, key: str):
        self.commands.append(("get", key, None))
        return self

    def set(self, key: str, value: float, ex: int | None = None):
        self.commands.append(("set", key, value))
        return self

    async def execute(self):
        results: list[float | bool | None] = []
        for command, key, value in self.commands:
            if command == "get":
                results.append(self.storage.get(key))
            elif command == "set":
                self.storage[key] = value if value is not None else 0.0
                results.append(True)
        self.commands.clear()
        return results


class FakeRedis:
    def __init__(self) -> None:
        self.storage: dict[str, float] = {}

    def pipeline(self) -> FakePipeline:
        return FakePipeline(self.storage)


def test_rate_limit_middleware_blocks_when_bucket_empty(monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(
        "kubemind_common.middleware.rate_limit.get_async_redis", lambda url: fake_redis
    )

    current_time = {"value": 1_000.0}

    def fake_time():
        return current_time["value"]

    monkeypatch.setattr("kubemind_common.middleware.rate_limit.time.time", fake_time)

    limiter = TokenBucketLimiter(
        key_prefix="test",
        capacity=2,
        refill_rate_per_sec=1.0,
        redis_url="redis://test",
    )

    app = FastAPI()
    app.middleware("http")(rate_limit_middleware(limiter))

    @app.get("/")
    async def pong():  # pragma: no cover - exercised via middleware
        return {"ok": True}

    with TestClient(app) as client:
        current_time["value"] = 1_000.0
        first = client.get("/")
        second = client.get("/")
        third = client.get("/")
        assert first.status_code == 200
        assert second.status_code == 200
        assert third.status_code == 429
        assert third.json()["detail"] == "Rate limit exceeded"

        current_time["value"] = 1_003.0
        fourth = client.get("/")
        assert fourth.status_code == 200
