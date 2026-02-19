"""Abstract notification channel interface.

Defines the contract that every event propagation channel must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class NotificationChannel(ABC):
    """Abstract base class for event notification channels.

    Each concrete channel represents a different propagation mechanism
    (HTTP webhook, internal service call, email, Slack, etc.).
    """

    @abstractmethod
    async def send(self, payload: Dict[str, Any]) -> None:
        """Send a notification with the given payload.

        Args:
            payload: Event data to propagate
        """
