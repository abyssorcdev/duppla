"""HTTP notification channel.

Sends event payloads via HTTP POST to any configured URL.
Supports custom headers per channel (e.g. auth tokens, content type).
"""

import logging
from typing import Any, Dict, Optional

from app.infrastructure.notifications.channels.base import NotificationChannel
from app.infrastructure.notifications.clients.http_client import HttpClient

logger = logging.getLogger(__name__)


class HttpNotificationChannel(NotificationChannel):
    """Notification channel that sends events via HTTP POST.

    Instantiated by the channel factory from a config entry of type 'http'.
    Receives name, url and optional headers from the NOTIFICATION_CHANNELS config list.
    """

    def __init__(self, name: str, url: str, headers: Optional[Dict[str, str]] = None) -> None:
        """Initialize with config values injected by the factory.

        Args:
            name: Human-readable identifier for logging
            url: Target URL to POST the event payload to
            headers: Optional HTTP headers to include in every request
        """
        self._name = name
        self._url = url
        self._headers = headers or {}
        self._client = HttpClient()

    async def send(self, payload: Dict[str, Any]) -> None:
        """Send the payload via HTTP POST.

        Args:
            payload: Event data to send
        """
        logger.info(f"Sending HTTP notification [{self._name}] → {self._url}")
        success = await self._client.post(self._url, payload, headers=self._headers)
        if not success:
            logger.error(f"HTTP notification [{self._name}] failed after retries: {self._url}")
