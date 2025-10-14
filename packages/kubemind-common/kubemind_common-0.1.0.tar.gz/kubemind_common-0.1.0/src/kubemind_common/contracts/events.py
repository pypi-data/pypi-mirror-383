from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Event(BaseModel):
    id: str = Field(..., description="Unique event id")
    version: str = Field(default="v1")
    source: str
    type: str
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    cluster_id: Optional[str] = None
    namespace: Optional[str] = None
    resource_kind: Optional[str] = None
    resource_name: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    context: Dict[str, Any] = Field(default_factory=dict)
    raw: Optional[Dict[str, Any]] = None

