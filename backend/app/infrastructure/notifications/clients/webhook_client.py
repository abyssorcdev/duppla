"""Webhook client for sending HTTP notifications.

Handles webhook delivery with retry logic.
"""

import logging
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


class WebhookClient:
    """Client for sending webhook notifications."""

    def __init__(self, timeout: int = 10) -> None:
        """Initialize webhook client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    async def send(self, url: str, payload: Dict[str, Any], max_retries: int = 3) -> bool:
        """Send webhook with exponential backoff retry.

        Args:
            url: Webhook URL
            payload: JSON payload to send
            max_retries: Maximum number of retry attempts

        Returns:
            True if successful, False otherwise
        """
        retry_delays = [2, 4, 8]

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()

                    logger.info(
                        f"Webhook sent successfully to {url}",
                        extra={"attempt": attempt + 1, "status_code": response.status_code},
                    )
                    return True

                except httpx.HTTPError as e:
                    logger.warning(
                        f"Webhook delivery failed (attempt {attempt + 1}/{max_retries}): {e}",
                        extra={"url": url, "error": str(e)},
                    )

                    if attempt < max_retries - 1:
                        import asyncio

                        await asyncio.sleep(retry_delays[attempt])

            logger.error(
                f"Webhook delivery failed after {max_retries} attempts",
                extra={"url": url},
            )
            return False
