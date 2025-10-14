from __future__ import annotations

import base64
from typing import Optional, Tuple


def parse_bearer(header_value: Optional[str]) -> Optional[str]:
    if not header_value:
        return None
    parts = header_value.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def parse_basic(header_value: Optional[str]) -> Optional[Tuple[str, str]]:
    if not header_value:
        return None
    parts = header_value.split()
    if len(parts) == 2 and parts[0].lower() == "basic":
        try:
            decoded = base64.b64decode(parts[1]).decode()
            user, pwd = decoded.split(":", 1)
            return user, pwd
        except Exception:
            return None
    return None

