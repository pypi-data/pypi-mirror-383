from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from prometheus_client import Counter, Histogram

task_total = Counter("tasks_total", "Total tasks", ["name", "status"])
task_duration = Histogram("task_duration_seconds", "Task duration", ["name"])


def instrument_task(name: str):
    def decorator(fn: Callable[..., Any]):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with task_duration.labels(name).time():
                try:
                    res = fn(*args, **kwargs)
                    task_total.labels(name, "success").inc()
                    return res
                except Exception:
                    task_total.labels(name, "error").inc()
                    raise

        return wrapper

    return decorator

