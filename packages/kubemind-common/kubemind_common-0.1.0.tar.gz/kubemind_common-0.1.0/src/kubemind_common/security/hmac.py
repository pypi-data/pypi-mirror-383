from __future__ import annotations

import hmac
from hashlib import sha256


def compute_hmac_sha256(secret: str, body: bytes) -> str:
    mac = hmac.new(secret.encode(), body, sha256).hexdigest()
    return mac


def verify_hmac_sha256(secret: str, body: bytes, signature: str) -> bool:
    expected = compute_hmac_sha256(secret, body)
    return hmac.compare_digest(expected, signature)

