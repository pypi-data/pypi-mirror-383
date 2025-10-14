import asyncio

import httpx

from kubemind_common.http.client import (
    create_http_client,
    http_get,
    http_post,
    http_request,
)


def test_create_http_client_defaults():
    client = create_http_client()
    assert isinstance(client, httpx.AsyncClient)
    assert client.headers["User-Agent"].startswith("kubemind")


def test_http_request_retry_with_mock_transport():
    attempts = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["n"] += 1
        if attempts["n"] < 2:
            # Simulate network error to trigger retry
            raise httpx.ConnectError("boom", request=request)
        return httpx.Response(status_code=200, json={"ok": True})

    transport = httpx.MockTransport(handler)

    async def flow():
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            res = await http_request(client, "GET", "/ping")
            assert res.status_code == 200
            assert res.json() == {"ok": True}

    asyncio.get_event_loop().run_until_complete(flow())


def test_http_get_post_helpers():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, json={"m": "g"})
        if request.method == "POST":
            import json as _json
            body = _json.loads(request.content.decode() or "{}")
            return httpx.Response(201, json=body)
        return httpx.Response(400)

    transport = httpx.MockTransport(handler)

    async def flow():
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as client:
            r1 = await http_get(client, "/x")
            assert r1.status_code == 200 and r1.json() == {"m": "g"}
            r2 = await http_post(client, "/x", json={"a": 1})
            assert r2.status_code == 201 and r2.json() == {"a": 1}

    asyncio.get_event_loop().run_until_complete(flow())
