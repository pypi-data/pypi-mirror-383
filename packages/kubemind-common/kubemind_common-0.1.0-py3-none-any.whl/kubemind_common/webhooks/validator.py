"""Webhook signature validation utilities."""
from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
    algorithm: str = "sha256"
) -> bool:
    """Verify HMAC signature of webhook payload.

    Args:
        payload: Raw request body bytes
        signature: Signature from webhook header
        secret: Shared secret key
        algorithm: Hash algorithm (default: sha256)

    Returns:
        True if signature is valid

    Example:
        body = await request.body()
        signature = request.headers.get("X-Webhook-Signature")
        if not verify_webhook_signature(body, signature, "secret"):
            raise HTTPException(status_code=401, detail="Invalid signature")
    """
    if not signature:
        return False

    # Compute expected signature
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        getattr(hashlib, algorithm)
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(signature, expected_signature)


def compute_webhook_signature(payload: bytes, secret: str, algorithm: str = "sha256") -> str:
    """Compute HMAC signature for webhook payload.

    Args:
        payload: Request body bytes
        secret: Shared secret key
        algorithm: Hash algorithm (default: sha256)

    Returns:
        HMAC signature (hexadecimal)

    Example:
        body = json.dumps(payload_dict).encode()
        signature = compute_webhook_signature(body, "secret")
        headers = {"X-Webhook-Signature": signature}
    """
    return hmac.new(
        secret.encode(),
        payload,
        getattr(hashlib, algorithm)
    ).hexdigest()


class WebhookValidator:
    """Webhook signature validator for FastAPI.

    Usage:
        webhook_validator = WebhookValidator(secret="your-secret-key")

        @app.post("/webhooks/incoming")
        async def receive_webhook(
            request: Request,
            validated: bool = Depends(webhook_validator.validate)
        ):
            body = await request.json()
            # Process webhook
            return {"status": "received"}
    """

    def __init__(
        self,
        secret: str,
        header_name: str = "X-Webhook-Signature",
        algorithm: str = "sha256",
        optional: bool = False
    ):
        """Initialize webhook validator.

        Args:
            secret: Shared secret key for HMAC
            header_name: HTTP header containing signature
            algorithm: Hash algorithm (sha256, sha1, sha512)
            optional: If True, skip validation if header missing
        """
        self.secret = secret
        self.header_name = header_name
        self.algorithm = algorithm
        self.optional = optional

    async def validate(self, request: Request) -> bool:
        """Validate webhook signature.

        Args:
            request: FastAPI request

        Returns:
            True if signature is valid

        Raises:
            HTTPException: If signature is invalid or missing
        """
        signature = request.headers.get(self.header_name)

        if not signature:
            if self.optional:
                logger.warning("Webhook signature header missing, but validation is optional")
                return False
            logger.error(f"Missing webhook signature header: {self.header_name}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Missing {self.header_name} header"
            )

        # Get raw body
        body = await request.body()

        # Verify signature
        is_valid = verify_webhook_signature(body, signature, self.secret, self.algorithm)

        if not is_valid:
            logger.error("Webhook signature validation failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )

        logger.debug("Webhook signature validated successfully")
        return True

    async def __call__(self, request: Request) -> bool:
        """Allow using validator as dependency directly.

        Args:
            request: FastAPI request

        Returns:
            True if valid
        """
        return await self.validate(request)


def create_webhook_validator(
    secret: str,
    header_name: str = "X-Webhook-Signature",
    algorithm: str = "sha256"
) -> callable:
    """Create a webhook validator dependency.

    Args:
        secret: Shared secret key
        header_name: HTTP header containing signature
        algorithm: Hash algorithm

    Returns:
        FastAPI dependency function

    Example:
        validate_github = create_webhook_validator(
            secret=settings.GITHUB_WEBHOOK_SECRET,
            header_name="X-Hub-Signature-256"
        )

        @app.post("/webhooks/github")
        async def github_webhook(
            request: Request,
            validated: bool = Depends(validate_github)
        ):
            ...
    """
    validator = WebhookValidator(secret, header_name, algorithm)
    return validator.validate
