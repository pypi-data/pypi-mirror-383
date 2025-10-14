from __future__ import annotations

import time
from typing import Callable

from starlette.requests import Request
from starlette.responses import Response

from kubemind_common.constants import HEADER_REQUEST_ID, HEADER_CORRELATION_ID
from kubemind_common.logging.setup import correlation_id_var


async def request_id_middleware(request: Request, call_next: Callable):
    request_id = request.headers.get(HEADER_REQUEST_ID) or request.headers.get(HEADER_CORRELATION_ID)
    token = None
    if request_id:
        token = correlation_id_var.set(request_id)
    start = time.perf_counter()
    try:
        response: Response = await call_next(request)
    finally:
        if token is not None:
            correlation_id_var.reset(token)
    # propagate header
    if request_id and isinstance(response, Response):
        response.headers.setdefault(HEADER_REQUEST_ID, request_id)
        response.headers.setdefault(HEADER_CORRELATION_ID, request_id)
    # add duration header
    duration = time.perf_counter() - start
    if isinstance(response, Response):
        response.headers["X-Process-Time"] = f"{duration:.3f}"
    return response

