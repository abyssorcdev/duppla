"""Notification clients package.

Contains low-level clients for sending event payloads (HTTP, SMS, etc).
"""

from app.infrastructure.notifications.clients.http_client import HttpClient

__all__ = ["HttpClient"]
