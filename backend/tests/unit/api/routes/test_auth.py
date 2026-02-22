"""Tests for app.api.routes.auth – Google OAuth routes."""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from tests.common import BaseTestCase

from app.domain.entities.user import UserStatus


class TestDependencyFunctions(BaseTestCase):
    """Tests for _get_auth_service dependency function."""

    def test_get_auth_service_success(self) -> None:
        from app.api.routes.auth import _get_auth_service
        from app.application.services.auth_service import AuthService

        result = _get_auth_service(db=MagicMock())
        self.assertIsInstance(result, AuthService)


class TestGoogleLogin(BaseTestCase):
    """Tests for GET /auth/google."""

    def test_google_login_success_redirects(self) -> None:
        from app.api.dependencies.database import get_database
        from app.api.routes.auth import _get_auth_service
        from app.main import app

        mock_auth = MagicMock()
        mock_auth.get_google_auth_url.return_value = "https://accounts.google.com/o/oauth2/v2/auth?foo=bar"

        app.dependency_overrides[get_database] = lambda: MagicMock()
        app.dependency_overrides[_get_auth_service] = lambda: mock_auth

        client = TestClient(app, follow_redirects=False)
        resp = client.get("/auth/google")
        self.assertEqual(resp.status_code, 307)
        self.assertIn("accounts.google.com", resp.headers["location"])
        app.dependency_overrides.clear()


class TestGoogleCallback(BaseTestCase):
    """Tests for GET /auth/google/callback."""

    def test_google_callback_success_redirects_with_token(self) -> None:
        from app.api.dependencies.database import get_database
        from app.api.routes.auth import _get_auth_service
        from app.main import app

        user = self.make_user(status=UserStatus.ACTIVE)
        mock_auth = MagicMock()
        mock_auth.exchange_code = AsyncMock(return_value={"access_token": "at123"})
        mock_auth.get_google_user_info = AsyncMock(return_value={
            "id": "gid", "email": user.email, "name": user.name,
        })
        mock_auth.find_or_create_user.return_value = user
        mock_auth.create_jwt.return_value = "jwt.token.here"

        app.dependency_overrides[get_database] = lambda: MagicMock()
        app.dependency_overrides[_get_auth_service] = lambda: mock_auth

        client = TestClient(app, follow_redirects=False)
        resp = client.get("/auth/google/callback?code=authcode123")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("token=jwt.token.here", resp.headers["location"])
        app.dependency_overrides.clear()

    def test_google_callback_error_oauth_failure(self) -> None:
        from app.api.dependencies.database import get_database
        from app.api.routes.auth import _get_auth_service
        from app.main import app

        mock_auth = MagicMock()
        mock_auth.exchange_code = AsyncMock(side_effect=Exception("oauth failed"))

        app.dependency_overrides[get_database] = lambda: MagicMock()
        app.dependency_overrides[_get_auth_service] = lambda: mock_auth

        client = TestClient(app, follow_redirects=False)
        resp = client.get("/auth/google/callback?code=bad")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("error=oauth_failed", resp.headers["location"])
        app.dependency_overrides.clear()


class TestGetMe(BaseTestCase):
    """Tests for GET /auth/me."""

    def test_get_me_returns_501(self) -> None:
        from app.api.dependencies.database import get_database
        from app.main import app

        app.dependency_overrides[get_database] = lambda: MagicMock()

        client = TestClient(app)
        resp = client.get("/auth/me")
        self.assertEqual(resp.status_code, 501)
        app.dependency_overrides.clear()
