"""Redis client for caching and rate limiting.

Provides API key validation cache and a generic sliding window rate limiter
usable for any identifier (API key, user ID, IP, etc.).
"""

import logging

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

_PREFIX_KEY_VALID = "apikey:valid:"
_PREFIX_RATE = "rl:"  # generic rate-limit prefix


class RedisClient:
    """Redis client with API key caching and generic rate limiting."""

    def __init__(self) -> None:
        self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    # -------------------------------------------------------------------------
    # API key cache
    # -------------------------------------------------------------------------

    def is_key_cached_valid(self, api_key: str) -> bool:
        """Return True if the key was previously validated and is still cached."""
        return self._client.exists(f"{_PREFIX_KEY_VALID}{api_key}") == 1

    def cache_valid_key(self, api_key: str) -> None:
        """Store a validated API key in cache with TTL."""
        self._client.setex(
            name=f"{_PREFIX_KEY_VALID}{api_key}",
            time=settings.API_KEY_CACHE_TTL,
            value="1",
        )

    def invalidate_key(self, api_key: str) -> None:
        """Remove a key from the valid cache (e.g. on revocation)."""
        self._client.delete(f"{_PREFIX_KEY_VALID}{api_key}")

    # -------------------------------------------------------------------------
    # Rate limiting
    # -------------------------------------------------------------------------

    def check_rate_limit(self, identifier: str) -> tuple[bool, int, int]:
        """Check whether *identifier* is within the configured rate limit.

        The identifier can be any string — API key, user UUID, IP address, etc.
        Uses a sliding window counter that resets automatically after
        RATE_LIMIT_WINDOW_SECONDS.

        Args:
            identifier: Unique key to track (e.g. "apikey:abc", "user:uuid")

        Returns:
            (allowed, current_count, retry_after_seconds)
            - allowed:       True if the request is within the limit
            - current_count: Requests made in the current window
            - retry_after:   Seconds until the window resets (0 if allowed)
        """
        rate_key = f"{_PREFIX_RATE}{identifier}"
        count = self._client.incr(rate_key)

        if count == 1:
            self._client.expire(rate_key, settings.RATE_LIMIT_WINDOW_SECONDS)

        allowed = count <= settings.RATE_LIMIT_REQUESTS
        retry_after = 0
        if not allowed:
            ttl = self._client.ttl(rate_key)
            retry_after = max(ttl, 1)

        return allowed, count, retry_after
