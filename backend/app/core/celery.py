"""Celery configuration for background tasks."""

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "transcriptok",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.workers.download_task",
        "app.workers.transcribe_task",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=540,  # Soft limit at 9 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
