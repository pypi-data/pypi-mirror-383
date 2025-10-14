from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional


def create_jwt(claims: Dict[str, Any], secret: str, algorithm: str = "HS256", expires_in: int = 3600) -> str:
    """Create a JWT (requires python-jose in the consuming environment)."""
    try:
        from jose import jwt
    except Exception as e:
        raise RuntimeError("python-jose is required to use create_jwt") from e
    payload = dict(claims)
    payload.setdefault("iat", int(datetime.now(timezone.utc).timestamp()))
    payload.setdefault("exp", int((datetime.now(timezone.utc) + timedelta(seconds=expires_in)).timestamp()))
    return jwt.encode(payload, secret, algorithm=algorithm)


def verify_jwt(token: str, secret: str, algorithms: Optional[list[str]] = None) -> Dict[str, Any]:
    try:
        from jose import jwt
    except Exception as e:
        raise RuntimeError("python-jose is required to use verify_jwt") from e
    return jwt.decode(token, secret, algorithms=algorithms or ["HS256"])

