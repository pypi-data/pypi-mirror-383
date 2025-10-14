from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    related_events: List[str] = Field(default_factory=list)


class InvestigationResponse(BaseModel):
    id: str
    summary: str
    findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    context_used: Dict[str, Any] = Field(default_factory=dict)

