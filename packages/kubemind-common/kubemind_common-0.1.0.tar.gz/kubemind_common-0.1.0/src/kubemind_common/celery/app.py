from __future__ import annotations

from celery import Celery


def create_celery_app(broker_url: str, result_backend: str) -> Celery:
    app = Celery("kubemind", broker=broker_url, backend=result_backend)
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        task_reject_on_worker_lost=True,
    )
    return app

