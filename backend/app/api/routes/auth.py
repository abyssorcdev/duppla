"""Authentication routes.

Handles Google OAuth2 flow:
  GET /auth/google          → redirect to Google consent screen
  GET /auth/google/callback → exchange code, issue JWT, redirect to frontend
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_database
from app.application.services.auth_service import AuthService
from app.core.config import settings
from app.infrastructure.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_auth_service(db: Session = Depends(get_database)) -> AuthService:
    return AuthService(UserRepository(db))


@router.get("/google", summary="Redirect to Google OAuth consent screen")
async def google_login(auth: AuthService = Depends(_get_auth_service)) -> RedirectResponse:
    """Initiates the Google OAuth2 flow by redirecting the user to Google."""
    url = auth.get_google_auth_url()
    return RedirectResponse(url=url)


@router.get("/google/callback", summary="Handle Google OAuth callback")
async def google_callback(
    code: str = Query(...),
    auth: AuthService = Depends(_get_auth_service),
) -> RedirectResponse:
    """Exchanges the authorization code, creates/finds the user and issues a JWT.

    On success, redirects to the frontend with the token and user status
    as query parameters so the frontend can store them and route accordingly.
    """
    try:
        token_data = await auth.exchange_code(code)
        access_token = token_data["access_token"]
        google_user = await auth.get_google_user_info(access_token)
    except Exception:
        logger.exception("Google OAuth exchange failed")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/callback?error=oauth_failed",
            status_code=status.HTTP_302_FOUND,
        )

    user = auth.find_or_create_user(
        google_id=google_user["id"],
        email=google_user["email"],
        name=google_user.get("name", google_user["email"]),
        picture=google_user.get("picture"),
    )

    jwt_token = auth.create_jwt(user)

    redirect_url = f"{settings.FRONTEND_URL}/auth/callback" f"?token={jwt_token}" f"&status={user.status.value}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.get("/me", summary="Get current authenticated user")
async def get_me(
    db: Session = Depends(get_database),
) -> None:
    """Returns the current user from the JWT. Used by the frontend on load."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
