from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ClusterConfig(BaseModel):
    id: str
    name: str
    in_cluster: bool = False
    kubeconfig_path: Optional[str] = None
    namespaces: List[str] = Field(default_factory=list)
    label_selectors: List[str] = Field(default_factory=list)
    enabled: bool = True

