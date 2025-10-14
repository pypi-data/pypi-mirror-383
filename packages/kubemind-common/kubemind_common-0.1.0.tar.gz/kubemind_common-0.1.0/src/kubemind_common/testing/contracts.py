from __future__ import annotations

from typing import Any, Dict

from pydantic import ValidationError as PydanticValidationError

from kubemind_common.contracts.events import Event


def assert_valid_event(obj: Dict[str, Any]) -> Event:
    try:
        return Event.model_validate(obj)
    except PydanticValidationError as exc:
        raise AssertionError(f"Invalid Event contract: {exc}") from exc

