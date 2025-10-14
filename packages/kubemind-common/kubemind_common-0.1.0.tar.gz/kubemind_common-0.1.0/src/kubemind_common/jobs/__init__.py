"""Background job abstractions for Celery tasks."""
from kubemind_common.jobs.base import BaseTask, TaskStatus

__all__ = [
    "BaseTask",
    "TaskStatus",
]
