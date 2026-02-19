"""Notifications infrastructure package.

Contains async task processing and notification delivery clients.
"""

from app.infrastructure.notifications.clients import HttpClient
from app.infrastructure.notifications.tasks import celery_app

__all__ = ["HttpClient", "celery_app"]
