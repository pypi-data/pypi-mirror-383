from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ActionSpec(BaseModel):
    name: Optional[str] = None
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[int] = None
    retry: Optional[Dict[str, Any]] = None
    on_error: Optional[str] = None  # stop|continue|retry|rollback
    output: Optional[str] = None
    when: Optional[str] = None


class PlaybookSpec(BaseModel):
    version: str = "1.0"
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    actions: List[ActionSpec] = Field(default_factory=list)

