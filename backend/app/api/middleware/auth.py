"""Authentication middleware for API Key validation.

Validates X-API-Key against configured keys, caches results in Redis,
and enforces per-key rate limiting with a sliding window counter.
"""

import logging
from typing import Optional

from fastapi import Header, HTTPException, Request, status

from app.core.config import settings
from app.infrastructure.cache.redis_client import RedisClient

logger = logging.getLogger(__name__)

_redis = RedisClient()


async def verify_api_key(request: Request, x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API Key from request header, with Redis cache and rate limiting.

    Flow:
        1. Reject if key is missing
        2. Check Redis cache → skip DB/config lookup if already validated
        3. Validate against settings if not cached → cache on success
        4. Check rate limit → reject with 429 if exceeded

    Args:
        x_api_key: API Key from X-API-Key header

    Returns:
        Validated API key

    Raises:
        HTTPException 401: If key is missing or invalid
        HTTPException 429: If rate limit is exceeded
    """

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required. Please provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    try:
        if not _redis.is_key_cached_valid(x_api_key):
            if x_api_key not in settings.API_KEYS_ALLOWED(method=request.method):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API Key for this request method.",
                    headers={"WWW-Authenticate": "ApiKey"},
                )
            _redis.cache_valid_key(x_api_key)
            logger.debug("API key cached after validation")

        allowed, count, retry_after = _redis.check_rate_limit(x_api_key)
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for key ...{x_api_key[-4:]}: "
                f"{count}/{settings.RATE_LIMIT_REQUESTS} requests "
                f"in {settings.RATE_LIMIT_WINDOW_SECONDS}s window — "
                f"retry in {retry_after}s"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Rate limit exceeded: {settings.RATE_LIMIT_REQUESTS} requests "
                    f"per {settings.RATE_LIMIT_WINDOW_SECONDS}s. "
                    f"Retry in {retry_after} second(s)."
                ),
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after),
                },
            )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Redis unavailable, falling back to direct key validation")
        if x_api_key not in settings.API_KEYS_ALLOWED(method=request.method):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key for this request method.",
                headers={"WWW-Authenticate": "ApiKey"},
            ) from None

    return x_api_key
