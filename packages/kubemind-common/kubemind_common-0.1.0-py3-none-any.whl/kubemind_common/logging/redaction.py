from __future__ import annotations

import logging
import re
from typing import Iterable


SENSITIVE_KEYS = {"authorization", "token", "password", "secret", "api_key", "apikey"}


class RedactingFilter(logging.Filter):
    """Redact sensitive values in log records (best-effort)."""

    def __init__(self, keys: Iterable[str] | None = None) -> None:
        super().__init__()
        keys = keys or SENSITIVE_KEYS
        pattern = r"(" + r"|".join(map(re.escape, keys)) + r")\s*[:=]\s*([^, ]+)"
        self._regex = re.compile(pattern, re.IGNORECASE)

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
            redacted = self._regex.sub(r"\1=<redacted>", msg)
            record.msg = redacted
        except Exception:
            pass
        return True

