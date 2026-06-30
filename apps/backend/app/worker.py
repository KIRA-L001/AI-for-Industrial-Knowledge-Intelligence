"""Celery application for asynchronous processing (OCR, extraction, embeddings).

Task modules are registered via `include` as each pipeline phase lands.
"""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "kira",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.document"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=60 * 30,
    worker_max_tasks_per_child=100,
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="kira.ping")
def ping() -> str:
    """Trivial task used to verify the worker is wired up."""
    return "pong"
