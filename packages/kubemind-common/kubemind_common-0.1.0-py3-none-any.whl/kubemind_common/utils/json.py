from __future__ import annotations

import json
from typing import Any, Iterable


def dumps_redacted(obj: Any, keys_to_redact: Iterable[str] | None = None) -> str:
    keys = {k.lower() for k in (keys_to_redact or ["authorization", "token", "password", "api_key"]) }

    def _redact(o):
        if isinstance(o, dict):
            return {k: ("<redacted>" if k.lower() in keys else _redact(v)) for k, v in o.items()}
        if isinstance(o, list):
            return [_redact(i) for i in o]
        return o

    return json.dumps(_redact(obj), ensure_ascii=False)

