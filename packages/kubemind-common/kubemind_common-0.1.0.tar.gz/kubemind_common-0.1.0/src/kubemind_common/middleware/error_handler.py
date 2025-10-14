from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import Request
from fastapi.responses import JSONResponse

from kubemind_common.exceptions import (
    KubemindError,
    ValidationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    AuthError,
)
from kubemind_common.errors.codes import ErrorCode
from kubemind_common.errors.schemas import ProblemDetails

logger = logging.getLogger(__name__)


async def problem_detail_handler(request: Request, exc: Exception) -> JSONResponse:
    status = 500
    title = "Internal Server Error"
    detail = str(exc)
    code = ErrorCode.INTERNAL_ERROR
    if isinstance(exc, ValidationError):
        status, title, code = 400, "Validation Error", ErrorCode.VALIDATION_ERROR
    elif isinstance(exc, NotFoundError):
        status, title, code = 404, "Not Found", ErrorCode.NOT_FOUND
    elif isinstance(exc, ConflictError):
        status, title, code = 409, "Conflict", ErrorCode.CONFLICT
    elif isinstance(exc, RateLimitError):
        status, title, code = 429, "Rate Limited", ErrorCode.RATE_LIMITED
    elif isinstance(exc, AuthError):
        status, title, code = 401, "Authentication Error", ErrorCode.AUTH_ERROR
    elif isinstance(exc, KubemindError):
        status, title, code = 400, exc.__class__.__name__, ErrorCode.VALIDATION_ERROR
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    body = ProblemDetails(title=title, status=status, detail=detail, code=code).model_dump()
    return JSONResponse(status_code=status, content=body)
