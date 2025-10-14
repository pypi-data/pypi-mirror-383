"""Action execution contracts and models."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ActionStatus(str, Enum):
    """Action execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class ActionErrorPolicy(str, Enum):
    """Action error handling policy."""
    STOP = "stop"          # Stop playbook execution
    CONTINUE = "continue"  # Continue to next action
    RETRY = "retry"        # Retry action with backoff
    ROLLBACK = "rollback"  # Rollback and stop


class ActionExecutionRecord(BaseModel):
    """Record of a single action execution."""

    execution_id: str = Field(description="Playbook execution ID")
    action_id: str = Field(description="Unique action execution ID")
    action_name: str = Field(description="Action name from playbook")
    action_type: str = Field(description="Action type/handler")
    status: ActionStatus = Field(description="Execution status")
    started_at: datetime = Field(description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    duration_ms: Optional[int] = Field(default=None, description="Execution duration in milliseconds")

    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    output: Optional[Dict[str, Any]] = Field(default=None, description="Action output")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    error_details: Optional[Dict[str, Any]] = Field(default=None, description="Detailed error information")

    retry_count: int = Field(default=0, description="Number of retry attempts")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True


class ActionResult(BaseModel):
    """Result of an action execution (lightweight for in-memory use)."""

    success: bool = Field(description="Whether action succeeded")
    output: Optional[Dict[str, Any]] = Field(default=None, description="Action output data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    duration_ms: Optional[int] = Field(default=None, description="Execution duration")
