"""Celery application configuration.

Configures Celery for async task processing.
"""

from celery import Celery

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "duppla",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Bogota",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.infrastructure.celery_tasks.*": {"queue": "default"},
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.infrastructure"])
