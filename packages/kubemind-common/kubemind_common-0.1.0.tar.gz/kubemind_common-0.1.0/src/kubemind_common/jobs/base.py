"""Base task class for Celery background jobs."""
from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Dict

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"


class BaseTask:
    """Base class for Celery tasks with logging and metrics.

    Usage:
        from celery import Celery
        from kubemind_common.jobs import BaseTask

        app = Celery("myapp")

        class ProcessDataTask(BaseTask):
            name = "tasks.process_data"

            def run(self, data_id: str) -> dict:
                self.log_info(f"Processing data {data_id}")
                # ... processing logic ...
                return {"status": "processed", "data_id": data_id}

        # Register with Celery
        @app.task(bind=True, base=ProcessDataTask)
        def process_data(self, data_id: str):
            return self.run(data_id)
    """

    name: str = "base_task"
    max_retries: int = 3
    retry_backoff: bool = True
    retry_backoff_max: int = 600
    retry_jitter: bool = True

    def __init__(self):
        """Initialize base task."""
        self.logger = logging.getLogger(f"tasks.{self.name}")
        self._start_time: float | None = None

    def before_start(self, task_id: str, args: tuple, kwargs: dict) -> None:
        """Hook called before task execution.

        Args:
            task_id: Celery task ID
            args: Task positional arguments
            kwargs: Task keyword arguments
        """
        self._start_time = time.time()
        self.log_info(f"Starting task {task_id}", extra={"task_id": task_id})

    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict) -> None:
        """Hook called on successful task execution.

        Args:
            retval: Task return value
            task_id: Celery task ID
            args: Task positional arguments
            kwargs: Task keyword arguments
        """
        duration = time.time() - self._start_time if self._start_time else 0
        self.log_info(
            f"Task {task_id} completed successfully in {duration:.2f}s",
            extra={"task_id": task_id, "duration": duration}
        )

    def on_failure(
        self,
        exc: Exception,
        task_id: str,
        args: tuple,
        kwargs: dict,
        einfo: Any
    ) -> None:
        """Hook called on task failure.

        Args:
            exc: Exception that caused failure
            task_id: Celery task ID
            args: Task positional arguments
            kwargs: Task keyword arguments
            einfo: Exception info
        """
        duration = time.time() - self._start_time if self._start_time else 0
        self.log_error(
            f"Task {task_id} failed after {duration:.2f}s: {exc}",
            exc_info=True,
            extra={"task_id": task_id, "duration": duration, "error": str(exc)}
        )

    def on_retry(
        self,
        exc: Exception,
        task_id: str,
        args: tuple,
        kwargs: dict,
        einfo: Any
    ) -> None:
        """Hook called when task is retried.

        Args:
            exc: Exception that triggered retry
            task_id: Celery task ID
            args: Task positional arguments
            kwargs: Task keyword arguments
            einfo: Exception info
        """
        self.log_warning(
            f"Task {task_id} retrying due to: {exc}",
            extra={"task_id": task_id, "error": str(exc)}
        )

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message.

        Args:
            message: Log message
            **kwargs: Additional logging context
        """
        self.logger.info(message, **kwargs)

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message.

        Args:
            message: Log message
            **kwargs: Additional logging context
        """
        self.logger.warning(message, **kwargs)

    def log_error(self, message: str, **kwargs: Any) -> None:
        """Log error message.

        Args:
            message: Log message
            **kwargs: Additional logging context
        """
        self.logger.error(message, **kwargs)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Main task execution method. Override in subclasses.

        Args:
            *args: Task arguments
            **kwargs: Task keyword arguments

        Returns:
            Task result
        """
        raise NotImplementedError("Subclasses must implement run()")


class PeriodicTask(BaseTask):
    """Base class for periodic/scheduled tasks.

    Usage:
        class DailyCleanupTask(PeriodicTask):
            name = "tasks.daily_cleanup"
            schedule_interval = 86400  # 24 hours

            def run(self):
                self.log_info("Running daily cleanup")
                # ... cleanup logic ...
                return {"cleaned": True}
    """

    schedule_interval: int | None = None  # Seconds between runs
    schedule_cron: Dict[str, Any] | None = None  # Crontab schedule

    def __init__(self):
        """Initialize periodic task."""
        super().__init__()


class RetryableTask(BaseTask):
    """Base class for tasks with custom retry logic.

    Usage:
        class FetchAPIDataTask(RetryableTask):
            name = "tasks.fetch_api_data"
            max_retries = 5
            retry_on = (ConnectionError, TimeoutError)

            def run(self, url: str):
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    return response.json()
                except self.retry_on as e:
                    self.retry(exc=e, countdown=60)
    """

    retry_on: tuple[type[Exception], ...] = (Exception,)
    default_retry_delay: int = 60  # Default retry delay in seconds

    def retry(
        self,
        exc: Exception | None = None,
        countdown: int | None = None,
        max_retries: int | None = None
    ) -> None:
        """Retry the task.

        Args:
            exc: Exception that triggered retry
            countdown: Seconds to wait before retry
            max_retries: Override max retries

        Note:
            This method should be called from within run() when using Celery bind=True.
            Example: self.retry(exc=e, countdown=60)
        """
        # This is a placeholder - actual implementation depends on Celery task instance
        # When using bind=True in Celery, self will have a retry() method
        raise NotImplementedError(
            "retry() should be called on Celery task instance with bind=True"
        )
