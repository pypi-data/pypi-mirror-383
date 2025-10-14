from __future__ import annotations

from celery import Celery


def celery_workers_count(app: Celery) -> int:
    try:
        stats = app.control.inspect().stats()
        return len(stats) if stats else 0
    except Exception:
        return 0

