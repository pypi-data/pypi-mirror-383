from __future__ import annotations

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from kubemind_common.middleware.request_id import request_id_middleware
from kubemind_common.middleware.request_logging import request_logging_middleware


async def homepage(request):
    return JSONResponse({"ok": True})


def create_app():
    app = Starlette(routes=[Route("/", homepage)])
    app.middleware("http")(request_id_middleware)
    app.middleware("http")(request_logging_middleware)
    return app


def test_middlewares_set_headers():
    app = create_app()
    client = TestClient(app)
    r = client.get("/", headers={"X-Request-ID": "abc-123"})
    assert r.status_code == 200
    assert r.headers.get("X-Request-ID") == "abc-123"
    assert r.headers.get("X-Process-Time") is not None
