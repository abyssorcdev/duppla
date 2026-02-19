"""Notification channel factory.

Builds channel instances from the NOTIFICATION_CHANNELS config list.
Registering a new channel type only requires adding it to CHANNEL_REGISTRY.
"""

import logging
from typing import Any, Dict, List, Type

from app.infrastructure.notifications.channels.base import NotificationChannel
from app.infrastructure.notifications.channels.http import HttpNotificationChannel

logger = logging.getLogger(__name__)


CHANNEL_REGISTRY: Dict[str, Type[NotificationChannel]] = {
    "http": HttpNotificationChannel,
}


def build_channels(config: List[Dict[str, Any]]) -> List[NotificationChannel]:
    """Instantiate notification channels from a config list.

    Each entry in config must have a 'type' key matching a registered channel.
    Remaining keys are passed as constructor arguments to the channel class.

    Args:
        config: List of channel config dicts from settings.NOTIFICATION_CHANNELS

    Returns:
        List of instantiated NotificationChannel objects
    """
    channels: List[NotificationChannel] = []

    for entry in config:
        channel_type = entry.get("type")
        channel_class = CHANNEL_REGISTRY.get(channel_type or "")

        if not channel_class:
            logger.warning(f"Unknown notification channel type '{channel_type}', skipping")
            continue

        params = {k: v for k, v in entry.items() if k != "type"}
        channels.append(channel_class(**params))

    return channels
