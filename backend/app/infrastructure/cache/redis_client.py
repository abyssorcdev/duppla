"""Redis client for caching and rate limiting.

Provides API key validation cache and sliding window rate limiting.
"""

import logging

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

_PREFIX_KEY_VALID = "apikey:valid:"
_PREFIX_RATE = "apikey:rate:"


class RedisClient:
    """Redis client with API key caching and rate limiting."""

    def __init__(self) -> None:
        self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    # -------------------------------------------------------------------------
    # API key cache
    # -------------------------------------------------------------------------

    def is_key_cached_valid(self, api_key: str) -> bool:
        """Check if a key was previously validated and is still cached.

        Args:
            api_key: The API key to check

        Returns:
            True if the key is in the valid cache
        """
        return self._client.exists(f"{_PREFIX_KEY_VALID}{api_key}") == 1

    def cache_valid_key(self, api_key: str) -> None:
        """Store a validated API key in cache with TTL.

        Args:
            api_key: The validated API key to cache
        """
        self._client.setex(
            name=f"{_PREFIX_KEY_VALID}{api_key}",
            time=settings.API_KEY_CACHE_TTL,
            value="1",
        )

    def invalidate_key(self, api_key: str) -> None:
        """Remove a key from the valid cache (e.g. on revocation).

        Args:
            api_key: The API key to remove
        """
        self._client.delete(f"{_PREFIX_KEY_VALID}{api_key}")

    # -------------------------------------------------------------------------
    # Rate limiting — sliding window counter
    # -------------------------------------------------------------------------

    def check_rate_limit(self, api_key: str) -> tuple[bool, int, int]:
        """Check if the API key is within its rate limit.

        Uses a sliding window counter: increments on each call and sets
        an expiry equal to the configured window. The counter resets
        automatically when the window expires.

        Args:
            api_key: The API key to check

        Returns:
            Tuple of (allowed, current_count, retry_after_seconds)
            - allowed: True if the request is within the rate limit
            - current_count: How many requests have been made in this window
            - retry_after_seconds: Seconds until the window resets (0 if allowed)
        """
        rate_key = f"{_PREFIX_RATE}{api_key}"

        count = self._client.incr(rate_key)

        if count == 1:
            self._client.expire(rate_key, settings.RATE_LIMIT_WINDOW_SECONDS)

        allowed = count <= settings.RATE_LIMIT_REQUESTS

        retry_after = 0
        if not allowed:
            ttl = self._client.ttl(rate_key)
            retry_after = max(ttl, 1)

        return allowed, count, retry_after
