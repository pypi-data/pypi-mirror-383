from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Notification(BaseModel):
    channel: str  # slack|email|webhook|pagerduty|jira|teams
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    target: Optional[str] = None  # channel name, email, URL, etc.

