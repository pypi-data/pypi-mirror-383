import asyncio

import pytest

from kubemind_common.resilience.retry import (
    retry_with_backoff,
    retry_with_tenacity,
)


def test_retry_with_backoff_on_sync_raises():
    @retry_with_backoff()
    def sync_fn():
        return 1

    with pytest.raises(RuntimeError):
        sync_fn()


def test_retry_with_backoff_succeeds_after_failures():
    attempts = {"n": 0}

    @retry_with_backoff(max_attempts=3, min_wait=0.01, max_wait=0.02, jitter=False, retry_on=RuntimeError)
    async def maybe_fail():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("fail")
        return "ok"

    res = asyncio.get_event_loop().run_until_complete(maybe_fail())
    assert res == "ok"
    assert attempts["n"] == 3


def test_retry_with_tenacity_preset_fast():
    calls = {"n": 0}

    @retry_with_tenacity(preset="fast")
    async def unstable():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("boom")
        return 42

    res = asyncio.get_event_loop().run_until_complete(unstable())
    assert res == 42
    assert calls["n"] == 2

