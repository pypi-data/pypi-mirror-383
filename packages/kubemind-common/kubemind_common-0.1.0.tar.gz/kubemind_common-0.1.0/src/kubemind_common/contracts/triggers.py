from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TriggerPlaybookRef(BaseModel):
    name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class Trigger(BaseModel):
    id: str
    name: str
    version: str = "v1"
    type: str  # event|schedule|manual|webhook
    priority: str = "normal"  # critical|high|normal|low
    enabled: bool = True
    conditions: Dict[str, Any] = Field(default_factory=dict)
    cooldown: Optional[int] = None
    rate_limit: Optional[Dict[str, Any]] = None
    playbooks: List[TriggerPlaybookRef] = Field(default_factory=list)

