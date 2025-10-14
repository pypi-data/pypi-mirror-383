"""API key generation, hashing, and validation utilities."""
from __future__ import annotations

import hashlib
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status


def generate_api_key(prefix: str = "km", length: int = 32) -> str:
    """Generate a secure random API key.

    Args:
        prefix: Key prefix for identification (e.g., "km" for KubeMind)
        length: Length of random portion (default: 32 bytes)

    Returns:
        API key string in format: {prefix}_{random_hex}

    Example:
        >>> key = generate_api_key(prefix="km", length=32)
        >>> print(key)
        km_a1b2c3d4e5f6...
    """
    random_bytes = secrets.token_bytes(length)
    random_hex = random_bytes.hex()
    return f"{prefix}_{random_hex}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA-256.

    Args:
        api_key: Plain text API key

    Returns:
        SHA-256 hash of the API key (hexadecimal)

    Example:
        >>> key = "km_abc123"
        >>> key_hash = hash_api_key(key)
        >>> # Store key_hash in database, never store plain key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def validate_api_key_format(api_key: str, prefix: str = "km") -> bool:
    """Validate API key format.

    Args:
        api_key: API key to validate
        prefix: Expected prefix

    Returns:
        True if format is valid

    Example:
        >>> validate_api_key_format("km_abc123def456")
        True
        >>> validate_api_key_format("invalid_key")
        False
    """
    if not api_key:
        return False

    parts = api_key.split("_", 1)
    if len(parts) != 2:
        return False

    key_prefix, key_value = parts
    if key_prefix != prefix:
        return False

    # Check if key value is hexadecimal
    try:
        int(key_value, 16)
        return True
    except ValueError:
        return False


async def get_api_key_from_header(request: Request) -> str:
    """Extract API key from X-API-Key header.

    Args:
        request: FastAPI request object

    Returns:
        API key string

    Raises:
        HTTPException: If API key is missing or invalid format

    Usage:
        from fastapi import Depends
        from kubemind_common.security.api_keys import get_api_key_from_header

        @app.get("/protected")
        async def protected_endpoint(api_key: str = Depends(get_api_key_from_header)):
            # api_key is validated format
            ...
    """
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not validate_api_key_format(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


def create_api_key_dependency(
    validator: callable | None = None,
    header_name: str = "X-API-Key"
) -> callable:
    """Create a FastAPI dependency for API key authentication.

    Args:
        validator: Optional async function to validate API key against database
                  Should raise HTTPException if invalid
        header_name: HTTP header name for API key (default: X-API-Key)

    Returns:
        FastAPI dependency function

    Example:
        from kubemind_common.security.api_keys import create_api_key_dependency

        async def validate_key(api_key: str):
            key_hash = hash_api_key(api_key)
            # Check database
            if not await db.api_key_exists(key_hash):
                raise HTTPException(status_code=401, detail="Invalid API key")
            return api_key

        require_api_key = create_api_key_dependency(validator=validate_key)

        @app.get("/api/data")
        async def get_data(api_key: str = Depends(require_api_key)):
            return {"message": "Authenticated with API key"}
    """
    async def dependency(request: Request) -> str:
        api_key = request.headers.get(header_name)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Missing {header_name} header",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        if not validate_api_key_format(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key format",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Call custom validator if provided
        if validator:
            await validator(api_key)

        return api_key

    return dependency


class APIKeyAuth:
    """API key authentication helper for FastAPI.

    Usage:
        from kubemind_common.security.api_keys import APIKeyAuth

        api_key_auth = APIKeyAuth(validator=validate_api_key_in_db)

        @app.get("/protected")
        async def protected_route(api_key: str = Depends(api_key_auth)):
            return {"message": "Authenticated"}
    """

    def __init__(
        self,
        validator: callable | None = None,
        header_name: str = "X-API-Key",
        prefix: str = "km"
    ):
        """Initialize API key auth.

        Args:
            validator: Optional async function to validate API key
            header_name: HTTP header name for API key
            prefix: Expected API key prefix
        """
        self.validator = validator
        self.header_name = header_name
        self.prefix = prefix

    async def __call__(self, request: Request) -> str:
        """Dependency callable for FastAPI.

        Args:
            request: FastAPI request

        Returns:
            Validated API key

        Raises:
            HTTPException: If authentication fails
        """
        api_key = request.headers.get(self.header_name)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Missing {self.header_name} header",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        if not validate_api_key_format(api_key, prefix=self.prefix):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key format",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Call custom validator if provided
        if self.validator:
            await self.validator(api_key)

        return api_key
