from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from kubemind_common.exceptions import (
    AuthError,
    ConflictError,
    ExternalServiceError,
    KubemindError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from kubemind_common.errors.codes import ErrorCode
from kubemind_common.middleware.error_handler import problem_detail_handler


@pytest.fixture(scope="module")
def error_app():
    app = FastAPI()

    exception_factories = {
        "validation": lambda: ValidationError("invalid payload"),
        "not_found": lambda: NotFoundError("missing resource"),
        "conflict": lambda: ConflictError("already exists"),
        "rate_limit": lambda: RateLimitError("too many requests"),
        "auth": lambda: AuthError("bad credentials"),
        "external_service": lambda: ExternalServiceError("upstream failure"),
        "generic_kubemind": lambda: KubemindError("generic kubemind error"),
        "generic_exception": lambda: Exception("unexpected failure"),
    }

    @app.get("/raise/{exc_name}")
    async def raise_error(exc_name: str):  # pragma: no cover - indirect testing target
        factory = exception_factories.get(exc_name)
        if not factory:
            raise ValueError(f"Unknown exception: {exc_name}")
        raise factory()

    app.add_exception_handler(Exception, problem_detail_handler)
    return app


@pytest.mark.parametrize(
    "path,expected_status,expected_title,expected_code,expected_detail",
    [
        ("validation", 400, "Validation Error", ErrorCode.VALIDATION_ERROR, "invalid payload"),
        ("not_found", 404, "Not Found", ErrorCode.NOT_FOUND, "missing resource"),
        ("conflict", 409, "Conflict", ErrorCode.CONFLICT, "already exists"),
        ("rate_limit", 429, "Rate Limited", ErrorCode.RATE_LIMITED, "too many requests"),
        ("auth", 401, "Authentication Error", ErrorCode.AUTH_ERROR, "bad credentials"),
        (
            "external_service",
            400,
            "ExternalServiceError",
            ErrorCode.VALIDATION_ERROR,
            "upstream failure",
        ),
        (
            "generic_kubemind",
            400,
            "KubemindError",
            ErrorCode.VALIDATION_ERROR,
            "generic kubemind error",
        ),
        (
            "generic_exception",
            500,
            "Internal Server Error",
            ErrorCode.INTERNAL_ERROR,
            "unexpected failure",
        ),
    ],
)
def test_problem_detail_handler_returns_expected_response(
    error_app: FastAPI,
    path: str,
    expected_status: int,
    expected_title: str,
    expected_code: str,
    expected_detail: str,
):
    with TestClient(error_app) as client:
        response = client.get(f"/raise/{path}")
    assert response.status_code == expected_status
    payload = response.json()
    assert payload["title"] == expected_title
    assert payload["code"] == expected_code
    assert payload["detail"] == expected_detail
    assert payload["status"] == expected_status
    assert payload["type"] == "about:blank"
