from __future__ import annotations

import asyncio

from starlette.requests import Request

from kubemind_common.middleware.error_handler import problem_detail_handler
from kubemind_common.exceptions import (
    KubemindError,
    ValidationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    AuthError,
)


def dummy_request() -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/x",
        "scheme": "http",
        "server": ("test", 80),
        "headers": [],
    }
    return Request(scope)


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_error_mapping_validation():
    resp = run(problem_detail_handler(dummy_request(), ValidationError("bad")))
    assert resp.status_code == 400


def test_error_mapping_not_found():
    resp = run(problem_detail_handler(dummy_request(), NotFoundError("missing")))
    assert resp.status_code == 404


def test_error_mapping_conflict():
    resp = run(problem_detail_handler(dummy_request(), ConflictError("conflict")))
    assert resp.status_code == 409


def test_error_mapping_rate_limited():
    resp = run(problem_detail_handler(dummy_request(), RateLimitError("limit")))
    assert resp.status_code == 429


def test_error_mapping_auth():
    resp = run(problem_detail_handler(dummy_request(), AuthError("auth")))
    assert resp.status_code == 401


def test_error_mapping_generic():
    resp = run(problem_detail_handler(dummy_request(), KubemindError("oops")))
    assert resp.status_code == 400
