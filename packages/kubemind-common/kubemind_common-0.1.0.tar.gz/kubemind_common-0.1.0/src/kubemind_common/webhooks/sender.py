"""Webhook sender with retry and signature support."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from kubemind_common.webhooks.validator import compute_webhook_signature

logger = logging.getLogger(__name__)


class WebhookSender:
    """Async webhook sender with automatic retries and signatures.

    Usage:
        sender = WebhookSender(secret="webhook-secret")

        await sender.send(
            url="https://example.com/webhook",
            payload={"event": "user.created", "data": {...}},
            headers={"X-Custom-Header": "value"}
        )
    """

    def __init__(
        self,
        secret: str | None = None,
        signature_header: str = "X-Webhook-Signature",
        timeout: float = 10.0,
        max_retries: int = 3
    ):
        """Initialize webhook sender.

        Args:
            secret: Shared secret for HMAC signatures (optional)
            signature_header: Header name for signature
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.secret = secret
        self.signature_header = signature_header
        self.timeout = timeout
        self.max_retries = max_retries

    async def send(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str] | None = None,
        method: str = "POST"
    ) -> httpx.Response:
        """Send webhook with automatic retry.

        Args:
            url: Webhook URL
            payload: JSON payload
            headers: Additional HTTP headers
            method: HTTP method (default: POST)

        Returns:
            HTTP response

        Raises:
            httpx.HTTPError: If all retries fail
        """
        headers = headers or {}

        # Compute signature if secret is provided
        if self.secret:
            import json
            body = json.dumps(payload, separators=(",", ":")).encode()
            signature = compute_webhook_signature(body, self.secret)
            headers[self.signature_header] = signature

        # Send with retry
        return await self._send_with_retry(url, payload, headers, method)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    async def _send_with_retry(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        method: str
    ) -> httpx.Response:
        """Send HTTP request with tenacity retry.

        Args:
            url: Webhook URL
            payload: JSON payload
            headers: HTTP headers
            method: HTTP method

        Returns:
            HTTP response

        Raises:
            httpx.HTTPError: On failure after retries
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            logger.debug(f"Sending webhook to {url}")

            response = await client.request(
                method=method,
                url=url,
                json=payload,
                headers=headers
            )

            # Raise for 4xx and 5xx status codes
            response.raise_for_status()

            logger.info(f"Webhook sent successfully to {url}: {response.status_code}")
            return response

    async def send_many(
        self,
        webhooks: list[Dict[str, Any]],
        concurrent: int = 5
    ) -> list[httpx.Response | Exception]:
        """Send multiple webhooks concurrently.

        Args:
            webhooks: List of webhook configs, each with 'url', 'payload', optional 'headers'
            concurrent: Maximum concurrent requests

        Returns:
            List of responses or exceptions

        Example:
            results = await sender.send_many([
                {"url": "https://a.com/hook", "payload": {"event": "test"}},
                {"url": "https://b.com/hook", "payload": {"event": "test"}},
            ])
        """
        semaphore = asyncio.Semaphore(concurrent)

        async def send_with_semaphore(webhook: Dict[str, Any]) -> httpx.Response | Exception:
            async with semaphore:
                try:
                    return await self.send(
                        url=webhook["url"],
                        payload=webhook["payload"],
                        headers=webhook.get("headers"),
                        method=webhook.get("method", "POST")
                    )
                except Exception as e:
                    logger.error(f"Failed to send webhook to {webhook['url']}: {e}")
                    return e

        tasks = [send_with_semaphore(webhook) for webhook in webhooks]
        return await asyncio.gather(*tasks)

    async def send_fire_and_forget(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str] | None = None
    ) -> None:
        """Send webhook without waiting for response (fire and forget).

        Args:
            url: Webhook URL
            payload: JSON payload
            headers: Additional HTTP headers

        Note:
            This method returns immediately. Errors are logged but not raised.
        """
        asyncio.create_task(self._fire_and_forget_task(url, payload, headers))

    async def _fire_and_forget_task(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str] | None
    ) -> None:
        """Background task for fire-and-forget webhooks.

        Args:
            url: Webhook URL
            payload: JSON payload
            headers: Additional HTTP headers
        """
        try:
            await self.send(url, payload, headers)
        except Exception as e:
            logger.error(f"Fire-and-forget webhook failed for {url}: {e}")
