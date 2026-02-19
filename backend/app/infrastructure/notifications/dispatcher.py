"""Notification dispatcher.

Broadcasts an event payload to all registered notification channels.
Use from_config() to build the dispatcher directly from settings.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.infrastructure.notifications.channels.base import NotificationChannel

logger = logging.getLogger(__name__)


@dataclass
class DispatchResult:
    """Result of a dispatch operation across all channels."""

    succeeded: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)

    @property
    def all_succeeded(self) -> bool:
        return len(self.failed) == 0

    def __str__(self) -> str:
        return f"succeeded={self.succeeded}, failed={self.failed}"


class NotificationDispatcher:
    """Dispatches event payloads to all registered notification channels.

    Channels are built from the NOTIFICATION_CHANNELS config list via from_config().
    The dispatcher is channel-agnostic — it only knows the shared NotificationChannel interface.

    Usage:
        dispatcher = NotificationDispatcher.from_config()
        await dispatcher.dispatch(payload)
    """

    def __init__(self, channels: List[NotificationChannel]) -> None:
        """Initialize dispatcher with a list of channels.

        Args:
            channels: Instantiated notification channels to dispatch to
        """
        self._channels = channels

    @classmethod
    def from_config(cls) -> "NotificationDispatcher":
        """Build a dispatcher from settings.NOTIFICATION_CHANNELS.

        Reads the unified channel config list and instantiates each channel
        via the factory based on its type.

        Returns:
            NotificationDispatcher ready to dispatch events
        """
        from app.core.config import settings
        from app.infrastructure.notifications.channels.factory import build_channels

        return cls(build_channels(settings.NOTIFICATION_CHANNELS))

    async def dispatch(self, payload: Dict[str, Any]) -> DispatchResult:
        """Send the payload to all registered channels.

        Failures in one channel do not stop the others.

        Args:
            payload: Event data to propagate

        Returns:
            DispatchResult with lists of succeeded and failed channel names
        """
        result = DispatchResult()

        for channel in self._channels:
            channel_name = getattr(channel, "_name", type(channel).__name__)
            try:
                await channel.send(payload)
                result.succeeded.append(channel_name)
                logger.info(f"Channel [{channel_name}] dispatched successfully")
            except Exception:
                result.failed.append(channel_name)
                logger.exception(f"Channel [{channel_name}] failed to dispatch notification")

        if not result.all_succeeded:
            logger.warning(f"Dispatch completed with failures: {result}")
        else:
            logger.info(f"Dispatch completed: all channels succeeded {result.succeeded}")

        return result
