from __future__ import annotations

from typing import Callable

from prometheus_client import Counter, Histogram
from starlette.requests import Request

http_requests_total = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds", "HTTP request duration seconds", ["method", "path"]
)


def prometheus_instrumentation_middleware():
    async def _mw(request: Request, call_next: Callable):
        method = request.method
        path = request.url.path
        with http_request_duration_seconds.labels(method, path).time():
            response = await call_next(request)
        http_requests_total.labels(method, path, str(response.status_code)).inc()
        return response

    return _mw

