"""Celery tasks configuration package.

Contains Celery application setup and task definitions.
"""

from app.infrastructure.notifications.tasks.celery_app import celery_app

__all__ = ["celery_app"]
