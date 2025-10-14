from __future__ import annotations

import logging
import time
from typing import Any, Dict

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from kubemind_common.constants import USER_AGENT

logger = logging.getLogger(__name__)


def create_http_client(
    timeout: float = 30.0,
    headers: Dict[str, str] | None = None,
    follow_redirects: bool = True,
    max_redirects: int = 10
) -> httpx.AsyncClient:
    """Create HTTP async client with default configuration.

    Args:
        timeout: Request timeout in seconds
        headers: Additional headers
        follow_redirects: Whether to follow redirects
        max_redirects: Maximum number of redirects to follow

    Returns:
        Configured httpx.AsyncClient

    Usage:
        async with create_http_client() as client:
            response = await client.get("https://api.example.com")
    """
    default_headers = {"User-Agent": USER_AGENT}
    if headers:
        default_headers.update(headers)

    return httpx.AsyncClient(
        timeout=timeout,
        headers=default_headers,
        follow_redirects=follow_redirects,
        max_redirects=max_redirects
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=0.3, max=3))
async def http_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    log_response: bool = True,
    **kwargs: Any
) -> httpx.Response:
    """Make HTTP request with automatic retry and logging.

    Args:
        client: httpx.AsyncClient instance
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        log_response: Whether to log response details
        **kwargs: Additional request parameters

    Returns:
        httpx.Response

    Raises:
        httpx.HTTPError: On request failure after retries

    Usage:
        async with create_http_client() as client:
            response = await http_request(client, "GET", "https://api.example.com")
    """
    start_time = time.time()

    try:
        logger.debug(f"HTTP {method} {url}")
        response = await client.request(method, url, **kwargs)

        duration = time.time() - start_time

        if log_response:
            logger.info(
                f"HTTP {method} {url} -> {response.status_code} ({duration:.2f}s)",
                extra={
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "duration": duration
                }
            )

        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"HTTP {method} {url} failed after {duration:.2f}s: {e}",
            extra={
                "method": method,
                "url": url,
                "duration": duration,
                "error": str(e)
            }
        )
        raise


async def http_get(client: httpx.AsyncClient, url: str, **kwargs: Any) -> httpx.Response:
    """Convenience method for GET requests.

    Args:
        client: httpx.AsyncClient instance
        url: Request URL
        **kwargs: Additional request parameters

    Returns:
        httpx.Response
    """
    return await http_request(client, "GET", url, **kwargs)


async def http_post(
    client: httpx.AsyncClient,
    url: str,
    json: Dict[str, Any] | None = None,
    **kwargs: Any
) -> httpx.Response:
    """Convenience method for POST requests.

    Args:
        client: httpx.AsyncClient instance
        url: Request URL
        json: JSON payload
        **kwargs: Additional request parameters

    Returns:
        httpx.Response
    """
    return await http_request(client, "POST", url, json=json, **kwargs)


async def http_put(
    client: httpx.AsyncClient,
    url: str,
    json: Dict[str, Any] | None = None,
    **kwargs: Any
) -> httpx.Response:
    """Convenience method for PUT requests.

    Args:
        client: httpx.AsyncClient instance
        url: Request URL
        json: JSON payload
        **kwargs: Additional request parameters

    Returns:
        httpx.Response
    """
    return await http_request(client, "PUT", url, json=json, **kwargs)


async def http_delete(client: httpx.AsyncClient, url: str, **kwargs: Any) -> httpx.Response:
    """Convenience method for DELETE requests.

    Args:
        client: httpx.AsyncClient instance
        url: Request URL
        **kwargs: Additional request parameters

    Returns:
        httpx.Response
    """
    return await http_request(client, "DELETE", url, **kwargs)

