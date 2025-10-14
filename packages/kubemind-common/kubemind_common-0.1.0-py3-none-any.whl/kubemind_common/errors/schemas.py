from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ProblemDetails(BaseModel):
    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: Optional[str] = None
    code: Optional[str] = None
    instance: Optional[str] = None
    extra: dict[str, Any] = Field(default_factory=dict)

