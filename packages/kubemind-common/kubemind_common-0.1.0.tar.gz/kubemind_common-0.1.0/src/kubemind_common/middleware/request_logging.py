from __future__ import annotations

import logging
import time
from typing import Callable

from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("request")


async def request_logging_middleware(request: Request, call_next: Callable):
    start = time.perf_counter()
    response: Response = await call_next(request)
    duration = time.perf_counter() - start
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} {duration:.3f}s"
    )
    return response

