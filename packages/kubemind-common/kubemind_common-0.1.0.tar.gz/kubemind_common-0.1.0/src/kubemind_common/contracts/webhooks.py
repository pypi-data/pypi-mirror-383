from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WebhookAuth(BaseModel):
    type: str = "bearer"  # bearer|basic|hmac|none
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    header: Optional[str] = None
    secret: Optional[str] = None


class WebhookConfig(BaseModel):
    id: str
    path: str
    enabled: bool = True
    authentication: WebhookAuth = Field(default_factory=WebhookAuth)
    transformation: Dict[str, Any] = Field(default_factory=dict)
    rate_limit: Optional[Dict[str, Any]] = None

