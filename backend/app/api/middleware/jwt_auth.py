"""JWT authentication middleware.

Provides FastAPI dependencies for user authentication and role-based
authorization using signed JWT tokens.
"""

import logging
import uuid
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_database
from app.core.config import settings
from app.domain.entities.user import User, UserRole, UserStatus
from app.infrastructure.cache.redis_client import RedisClient
from app.infrastructure.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
_redis = RedisClient()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_database),
) -> User:
    """Decode JWT and return the authenticated user.

    Raises 401 if token is missing, invalid or expired.
    Raises 403 if user account is disabled.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        from app.application.services.auth_service import AuthService

        auth_svc = AuthService(UserRepository(db))
        payload = auth_svc.decode_jwt(token)
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise ValueError("Missing subject in token")
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError) as exc:
        logger.warning("JWT validation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    repo = UserRepository(db)
    user = repo.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    if user.status == UserStatus.DISABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been disabled.",
        )

    try:
        allowed, count, retry_after = _redis.check_rate_limit(f"user:{user_id}")
        if not allowed:
            logger.warning(
                "Rate limit exceeded for user %s: %d/%d requests in %ds window",
                user_id,
                count,
                settings.RATE_LIMIT_REQUESTS,
                settings.RATE_LIMIT_WINDOW_SECONDS,
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
        logger.warning("Redis unavailable for rate limiting, skipping check for user %s", user_id)

    return user


def require_roles(*roles: UserRole) -> Callable:
    """Dependency factory that enforces role-based access.

    Usage:
        @router.post("/", dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.LOADER))])
    """

    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.status == UserStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is pending admin approval.",
            )
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {[r.value for r in roles]}",
            )
        return user

    return _check


# ── Convenience shorthands ────────────────────────────────────────────────────


def require_any_active_role() -> Callable:
    """Allow any user with an active account (any role)."""
    return require_roles(UserRole.ADMIN, UserRole.LOADER, UserRole.APPROVER)


def require_admin() -> Callable:
    return require_roles(UserRole.ADMIN)


def require_loader() -> Callable:
    return require_roles(UserRole.ADMIN, UserRole.LOADER)


def require_approver() -> Callable:
    return require_roles(UserRole.ADMIN, UserRole.APPROVER)
