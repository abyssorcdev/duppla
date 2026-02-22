"""Tests for app.api.middleware.jwt_auth."""

import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from tests.common import BaseTestCase

from app.domain.entities.user import UserRole, UserStatus


class TestGetCurrentUser(BaseTestCase):
    """Tests for get_current_user()."""

    def _run(self, token, db=None):
        from app.api.middleware.jwt_auth import get_current_user

        return asyncio.run(get_current_user(token=token, db=db or MagicMock()))

    def test_get_current_user_error_no_token(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            self._run(None)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_get_current_user_error_invalid_token(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            self._run("bad.token.string")
        self.assertEqual(ctx.exception.status_code, 401)

    @patch("app.api.middleware.jwt_auth._redis")
    @patch("app.api.middleware.jwt_auth.UserRepository")
    @patch("app.application.services.auth_service.AuthService.decode_jwt")
    def test_get_current_user_success_valid_token(self, mock_decode, MockUserRepo, mock_redis) -> None:
        user = self.make_user(status=UserStatus.ACTIVE)
        mock_decode.return_value = {"sub": str(user.id), "email": user.email}
        MockUserRepo.return_value.find_by_id.return_value = user
        mock_redis.check_rate_limit.return_value = (True, 1, 0)

        result = self._run("valid-token", MagicMock())
        self.assertEqual(result.email, user.email)

    @patch("app.api.middleware.jwt_auth._redis")
    @patch("app.api.middleware.jwt_auth.UserRepository")
    @patch("app.application.services.auth_service.AuthService.decode_jwt")
    def test_get_current_user_error_user_not_found(self, mock_decode, MockUserRepo, mock_redis) -> None:
        mock_decode.return_value = {"sub": str(self.fake.uuid4())}
        MockUserRepo.return_value.find_by_id.return_value = None

        with self.assertRaises(HTTPException) as ctx:
            self._run("valid-token", MagicMock())
        self.assertEqual(ctx.exception.status_code, 401)

    @patch("app.api.middleware.jwt_auth._redis")
    @patch("app.api.middleware.jwt_auth.UserRepository")
    @patch("app.application.services.auth_service.AuthService.decode_jwt")
    def test_get_current_user_error_disabled_user(self, mock_decode, MockUserRepo, mock_redis) -> None:
        user = self.make_user(status=UserStatus.DISABLED)
        mock_decode.return_value = {"sub": str(user.id)}
        MockUserRepo.return_value.find_by_id.return_value = user

        with self.assertRaises(HTTPException) as ctx:
            self._run("valid-token", MagicMock())
        self.assertEqual(ctx.exception.status_code, 403)

    @patch("app.api.middleware.jwt_auth._redis")
    @patch("app.api.middleware.jwt_auth.UserRepository")
    @patch("app.application.services.auth_service.AuthService.decode_jwt")
    def test_get_current_user_error_rate_limited(self, mock_decode, MockUserRepo, mock_redis) -> None:
        user = self.make_user(status=UserStatus.ACTIVE)
        mock_decode.return_value = {"sub": str(user.id)}
        MockUserRepo.return_value.find_by_id.return_value = user
        mock_redis.check_rate_limit.return_value = (False, 200, 30)

        with self.assertRaises(HTTPException) as ctx:
            self._run("valid-token", MagicMock())
        self.assertEqual(ctx.exception.status_code, 429)

    @patch("app.api.middleware.jwt_auth._redis")
    @patch("app.api.middleware.jwt_auth.UserRepository")
    @patch("app.application.services.auth_service.AuthService.decode_jwt")
    def test_get_current_user_success_redis_down_skips_rate_limit(self, mock_decode, MockUserRepo, mock_redis) -> None:
        user = self.make_user(status=UserStatus.ACTIVE)
        mock_decode.return_value = {"sub": str(user.id)}
        MockUserRepo.return_value.find_by_id.return_value = user
        mock_redis.check_rate_limit.side_effect = ConnectionError("redis down")

        result = self._run("valid-token", MagicMock())
        self.assertEqual(result.email, user.email)

    @patch("app.application.services.auth_service.AuthService.decode_jwt")
    def test_get_current_user_error_missing_sub_in_token(self, mock_decode) -> None:
        mock_decode.return_value = {"email": "test@test.com"}
        with self.assertRaises(HTTPException) as ctx:
            self._run("token-no-sub", MagicMock())
        self.assertEqual(ctx.exception.status_code, 401)


class TestRequireRoles(BaseTestCase):
    """Tests for require_roles() factory."""

    def test_require_roles_success_matching_role(self) -> None:
        from app.api.middleware.jwt_auth import require_roles

        check_fn = require_roles(UserRole.ADMIN, UserRole.LOADER)
        user = self.make_user(role=UserRole.ADMIN, status=UserStatus.ACTIVE)
        result = asyncio.run(check_fn(user))
        self.assertEqual(result, user)

    def test_require_roles_error_wrong_role(self) -> None:
        from app.api.middleware.jwt_auth import require_roles

        check_fn = require_roles(UserRole.ADMIN)
        user = self.make_user(role=UserRole.LOADER, status=UserStatus.ACTIVE)
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(check_fn(user))
        self.assertEqual(ctx.exception.status_code, 403)

    def test_require_roles_error_pending_user(self) -> None:
        from app.api.middleware.jwt_auth import require_roles

        check_fn = require_roles(UserRole.ADMIN)
        user = self.make_user(role=UserRole.ADMIN, status=UserStatus.PENDING)
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(check_fn(user))
        self.assertEqual(ctx.exception.status_code, 403)


class TestConvenienceShorthands(BaseTestCase):
    """Tests for require_any_active_role, require_admin, etc."""

    def test_require_any_active_role_returns_callable(self) -> None:
        from app.api.middleware.jwt_auth import require_any_active_role

        fn = require_any_active_role()
        self.assertTrue(callable(fn))

    def test_require_admin_returns_callable(self) -> None:
        from app.api.middleware.jwt_auth import require_admin

        fn = require_admin()
        self.assertTrue(callable(fn))

    def test_require_loader_returns_callable(self) -> None:
        from app.api.middleware.jwt_auth import require_loader

        fn = require_loader()
        self.assertTrue(callable(fn))

    def test_require_approver_returns_callable(self) -> None:
        from app.api.middleware.jwt_auth import require_approver

        fn = require_approver()
        self.assertTrue(callable(fn))
