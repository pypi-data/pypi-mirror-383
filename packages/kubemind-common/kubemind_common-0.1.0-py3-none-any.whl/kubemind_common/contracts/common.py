from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class HealthStatus(BaseModel):
    status: str
    service: str
    version: Optional[str] = None
    message: Optional[str] = None


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int

