from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ActionResult(BaseModel):
    name: Optional[str] = None
    action: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class Execution(BaseModel):
    id: str
    playbook_id: str
    status: str = "pending"  # pending|running|completed|failed|cancelled
    event_id: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    duration: Optional[float] = None
    outputs: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    action_results: List[ActionResult] = Field(default_factory=list)

