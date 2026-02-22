"""Authentication service.

Handles Google OAuth2 flow and JWT token management.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
from jose import jwt

from app.core.config import settings
from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"  # noqa: S105
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class AuthService:
    """Orchestrates Google OAuth and JWT lifecycle."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    # ── Google OAuth ──────────────────────────────────────────────────────────

    def get_google_auth_url(self) -> str:
        """Build the Google consent screen URL."""
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account",
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for Google tokens."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """Fetch user profile from Google."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            return resp.json()

    # ── User management ───────────────────────────────────────────────────────

    def find_or_create_user(
        self,
        google_id: str,
        email: str,
        name: str,
        picture: Optional[str],
    ) -> User:
        """Find existing user or register a new pending one."""
        user = self._repo.find_by_google_id(google_id)
        if user:
            return user
        logger.info("New user registered via Google OAuth: %s", email)
        return self._repo.create(google_id=google_id, email=email, name=name, picture=picture)

    # ── JWT ───────────────────────────────────────────────────────────────────

    def create_jwt(self, user: User) -> str:
        """Generate a signed JWT for the given user."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
            "role": user.role.value if user.role else None,
            "status": user.status.value,
            "iat": now,
            "exp": now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_jwt(self, token: str) -> Dict[str, Any]:
        """Decode and validate a JWT. Raises JWTError on failure."""
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
