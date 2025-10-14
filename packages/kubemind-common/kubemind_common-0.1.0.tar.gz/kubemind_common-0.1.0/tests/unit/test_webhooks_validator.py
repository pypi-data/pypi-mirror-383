import asyncio
import json

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from kubemind_common.webhooks.validator import (
    WebhookValidator,
    compute_webhook_signature,
    verify_webhook_signature,
)


def test_compute_and_verify_signature():
    body = json.dumps({"a": 1}).encode()
    secret = "sec"
    sig = compute_webhook_signature(body, secret)
    assert verify_webhook_signature(body, sig, secret)
    assert not verify_webhook_signature(body, "bad", secret)


def test_webhook_validator_missing_header_optional_and_required():
    validator_optional = WebhookValidator(secret="s", optional=True)
    validator_required = WebhookValidator(secret="s", optional=False)

    async def flow():
        req = Request({"type": "http", "method": "POST", "path": "/", "headers": []})
        # optional returns False
        ok = await validator_optional.validate(req)
        assert ok is False
        # required raises
        with pytest.raises(Exception):
            await validator_required.validate(req)

    asyncio.get_event_loop().run_until_complete(flow())


def test_webhook_validator_end_to_end():
    validator = WebhookValidator(secret="secret")

    async def endpoint(request: Request):
        await validator.validate(request)
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/webhook", endpoint, methods=["POST"])])
    body_dict = {"hello": "world"}
    body = json.dumps(body_dict, separators=(",", ":")).encode()
    signature = compute_webhook_signature(body, "secret")

    client = TestClient(app)
    r = client.post(
        "/webhook",
        data=body,
        headers={"X-Webhook-Signature": signature, "Content-Type": "application/json"},
    )
    assert r.status_code == 200
    assert r.json() == {"ok": True}

