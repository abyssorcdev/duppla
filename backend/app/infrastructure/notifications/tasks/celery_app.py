"""Celery application configuration.

Configures Celery for async task processing.
"""

from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger

from app.core.config import settings
from app.core.logging import setup_logging

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
    worker_hijack_root_logger=False,
    task_routes={
        "app.infrastructure.celery_tasks.*": {"queue": "default"},
    },
)


@after_setup_logger.connect
@after_setup_task_logger.connect
def configure_logging(*args, **kwargs) -> None:  # noqa: ANN002, ANN003
    """Re-apply our logging config after Celery finishes its own setup."""
    setup_logging(settings.LOG_LEVEL)


# Auto-discover tasks
celery_app.autodiscover_tasks(["app.infrastructure"])
