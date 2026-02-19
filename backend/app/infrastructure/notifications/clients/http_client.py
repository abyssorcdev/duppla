"""HTTP client for sending JSON notifications.

Generic HTTP POST client with exponential backoff retry logic.
Used by notification channels to deliver event payloads.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class HttpClient:
    """Generic HTTP client for sending JSON payloads via POST.

    Handles delivery with exponential backoff retry logic.
    """

    def __init__(self, timeout: int = 10) -> None:
        """Initialize client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    async def post(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
    ) -> bool:
        """Send a JSON payload via HTTP POST with exponential backoff retry.

        Args:
            url: Target URL
            payload: JSON payload to send
            headers: Optional HTTP headers to include in the request
            max_retries: Maximum number of retry attempts

        Returns:
            True if successful, False after exhausting all retries
        """
        retry_delays = [2, 4, 8]

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()

                    logger.info(
                        f"HTTP POST succeeded → {url}",
                        extra={"attempt": attempt + 1, "status_code": response.status_code},
                    )
                    return True

                except httpx.HTTPError as e:
                    logger.warning(
                        f"HTTP POST failed (attempt {attempt + 1}/{max_retries}): {e}",
                        extra={"url": url, "error": str(e)},
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delays[attempt])

        logger.error(f"HTTP POST failed after {max_retries} attempts → {url}")
        return False
