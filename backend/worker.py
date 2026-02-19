"""Celery worker entry point.

Run with:
    celery -A worker.celery_app worker --loglevel=info
    celery -A worker.celery_app worker --loglevel=info --concurrency=4
"""

from app.core.config import settings
from app.core.logging import setup_logging
from app.infrastructure.notifications.tasks.celery_app import celery_app
from app.infrastructure.notifications.tasks.document_tasks import process_documents_batch  # noqa: F401

setup_logging(settings.LOG_LEVEL)

__all__ = ["celery_app"]
