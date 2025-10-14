from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple, TypeVar

from kubemind_common.contracts.common import Page

T = TypeVar("T")


def parse_pagination(page: int | None, size: int | None, default_size: int = 50, max_size: int = 500) -> Tuple[int, int]:
    p = page or 1
    s = size or default_size
    if p < 1:
        p = 1
    if s < 1:
        s = 1
    if s > max_size:
        s = max_size
    return p, s


def paginate(items: Sequence[T], total: int, page: int, size: int) -> Page[T]:
    return Page[T](items=list(items), total=total, page=page, size=size)

