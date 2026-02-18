"""Celery tasks configuration package.

Contains Celery application setup and task definitions.
"""

from app.infrastructure.notifications.tasks.celery_app import celery_app
from app.infrastructure.notifications.tasks.document_tasks import process_documents_batch

__all__ = ["celery_app", "process_documents_batch"]
