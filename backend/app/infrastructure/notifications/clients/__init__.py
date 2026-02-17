"""Notification clients package.

Contains clients for sending notifications (webhooks, emails, SMS, etc).
"""

from app.infrastructure.notifications.clients.webhook_client import WebhookClient

__all__ = ["WebhookClient"]
