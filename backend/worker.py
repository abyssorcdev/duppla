"""Celery worker entry point.

Run with:
    celery -A worker.celery_app worker --loglevel=info
    celery -A worker.celery_app worker --loglevel=info --concurrency=4
"""

from app.infrastructure.notifications.tasks.celery_app import celery_app
from app.infrastructure.notifications.tasks.document_tasks import process_documents_batch  # noqa: F401

__all__ = ["celery_app"]
