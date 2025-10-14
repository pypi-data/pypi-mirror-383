from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Alert(BaseModel):
    id: str
    fingerprint: str
    name: Optional[str] = None
    status: str = Field(default="firing")  # firing|resolved
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, Any] = Field(default_factory=dict)
    severity: Optional[str] = None
    starts_at: Optional[str] = None
    ends_at: Optional[str] = None
    last_updated_at: Optional[str] = None
    duration_seconds: Optional[float] = None

