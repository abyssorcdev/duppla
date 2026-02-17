"""Authentication middleware for API Key validation.

Validates X-API-Key header against configured API keys.
"""

from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API Key from request header.

    Args:
        x_api_key: API Key from X-API-Key header

    Returns:
        Validated API Key

    Raises:
        HTTPException: If API Key is missing or invalid (401)
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required. Please provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    valid_keys = settings.API_KEYS.split(",") if settings.API_KEYS else []
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return x_api_key
