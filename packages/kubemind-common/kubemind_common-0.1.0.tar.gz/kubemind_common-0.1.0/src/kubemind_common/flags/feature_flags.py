from __future__ import annotations

from pydantic import BaseModel, Field


class FeatureFlags(BaseModel):
    auto_remediation: bool = Field(default=False)
    shell_actions_enabled: bool = Field(default=False)
    webhooks_enabled: bool = Field(default=True)
    scheduler_enabled: bool = Field(default=True)

