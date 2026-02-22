"""Tests for app.application.services.auth_service.AuthService."""

import unittest
from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase

from app.application.services.auth_service import AuthService
from app.domain.entities.user import User, UserRole, UserStatus


class AuthServiceTestCase(BaseTestCase):
    """Global base class for ALL AuthService tests."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.patcher_settings = patch("app.application.services.auth_service.settings")
        cls.mock_settings = cls.patcher_settings.start()
        cls.mock_settings.GOOGLE_CLIENT_ID = cls.fake.bothify("client-id-########")
        cls.mock_settings.GOOGLE_REDIRECT_URI = "http://localhost:8000/auth/google/callback"
        cls.mock_settings.GOOGLE_SECRET_KEY = cls.fake.password()
        cls.mock_settings.JWT_SECRET_KEY = cls.fake.password()
        cls.mock_settings.JWT_ALGORITHM = "HS256"
        cls.mock_settings.JWT_EXPIRE_MINUTES = 60

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.patcher_settings.stop()

    def setUp(self) -> None:
        super().setUp()
        self.mock_user_repo = MagicMock()
        self.service = AuthService(user_repo=self.mock_user_repo)

    def tearDown(self) -> None:
        super().tearDown()
        self.mock_user_repo.reset_mock()


class TestUnderScoreUnderScoreInit(AuthServiceTestCase):
    """Tests for __init__()."""

    def test_init_success_sets_repo(self) -> None:
        """
        When: AuthService is initialized with user_repo
        Then: Should store _repo attribute
        """
        service = AuthService(user_repo=self.mock_user_repo)
        self.assertEqual(service._repo, self.mock_user_repo)

    def test_init_success_accepts_mock(self) -> None:
        """
        When: Initialized with MagicMock
        Then: Should not raise
        """
        service = AuthService(user_repo=MagicMock())
        self.assertIsNotNone(service)

    def test_init_success_stores_reference(self) -> None:
        """
        When: Initialized with a repo
        Then: Should keep reference
        """
        repo = MagicMock()
        service = AuthService(user_repo=repo)
        self.assertIs(service._repo, repo)


class TestGetGoogleAuthUrl(AuthServiceTestCase):
    """Tests for get_google_auth_url()."""

    def test_get_google_auth_url_success_contains_base_url(self) -> None:
        """
        When: get_google_auth_url() is called
        Then: Should contain Google OAuth base URL
        """
        url = self.service.get_google_auth_url()
        self.assertIn("accounts.google.com", url)

    def test_get_google_auth_url_success_contains_client_id(self) -> None:
        """
        When: get_google_auth_url() is called
        Then: Should contain client_id parameter
        """
        url = self.service.get_google_auth_url()
        self.assertIn(f"client_id={self.mock_settings.GOOGLE_CLIENT_ID}", url)

    def test_get_google_auth_url_success_contains_redirect_uri(self) -> None:
        """
        When: get_google_auth_url() is called
        Then: Should contain redirect_uri parameter
        """
        url = self.service.get_google_auth_url()
        self.assertIn("redirect_uri=", url)

    def test_get_google_auth_url_success_contains_response_type(self) -> None:
        """
        When: get_google_auth_url() is called
        Then: Should contain response_type=code
        """
        url = self.service.get_google_auth_url()
        self.assertIn("response_type=code", url)

    def test_get_google_auth_url_success_contains_scope(self) -> None:
        """
        When: get_google_auth_url() is called
        Then: Should include openid, email, and profile scopes
        """
        url = self.service.get_google_auth_url()
        self.assertIn("scope=", url)
        self.assertIn("openid", url)


class TestFindOrCreateUser(AuthServiceTestCase):
    """Tests for find_or_create_user()."""

    def test_find_or_create_user_success_existing_user(self) -> None:
        """
        When: User with given google_id already exists
        Then: Should return existing user
        """
        google_id = self.fake.bothify("google-########")
        email = self.fake.email()
        name = self.fake.name()
        existing_user = self.make_user()
        self.mock_user_repo.find_by_google_id.return_value = existing_user

        result = self.service.find_or_create_user(
            google_id=google_id,
            email=email,
            name=name,
            picture=None,
        )

        self.assertEqual(result, existing_user)
        self.mock_user_repo.create.assert_not_called()

    def test_find_or_create_user_success_new_user(self) -> None:
        """
        When: User does not exist
        Then: Should create and return new user
        """
        google_id = self.fake.bothify("google-########")
        email = self.fake.email()
        name = self.fake.name()
        picture = self.fake.image_url()
        self.mock_user_repo.find_by_google_id.return_value = None
        new_user = self.make_user(status=UserStatus.PENDING, role=None)
        self.mock_user_repo.create.return_value = new_user

        result = self.service.find_or_create_user(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
        )

        self.assertEqual(result, new_user)
        self.mock_user_repo.create.assert_called_once()

    def test_find_or_create_user_success_create_args(self) -> None:
        """
        When: New user is created
        Then: Should pass correct args to repo.create
        """
        google_id = self.fake.bothify("google-########")
        email = self.fake.email()
        name = self.fake.name()
        picture = self.fake.image_url()
        self.mock_user_repo.find_by_google_id.return_value = None
        self.mock_user_repo.create.return_value = self.make_user()

        self.service.find_or_create_user(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
        )

        self.mock_user_repo.create.assert_called_once_with(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
        )

    def test_find_or_create_user_success_without_picture(self) -> None:
        """
        When: Picture is None
        Then: Should still work
        """
        google_id = self.fake.bothify("google-########")
        email = self.fake.email()
        name = self.fake.first_name()
        self.mock_user_repo.find_by_google_id.return_value = None
        self.mock_user_repo.create.return_value = self.make_user(picture=None)

        result = self.service.find_or_create_user(
            google_id=google_id,
            email=email,
            name=name,
            picture=None,
        )

        self.assertIsNotNone(result)

    def test_find_or_create_user_success_calls_find_first(self) -> None:
        """
        When: find_or_create_user() is called
        Then: Should check find_by_google_id before create
        """
        google_id = self.fake.bothify("google-########")
        email = self.fake.email()
        name = self.fake.first_name()
        self.mock_user_repo.find_by_google_id.return_value = self.make_user()

        self.service.find_or_create_user(
            google_id=google_id,
            email=email,
            name=name,
            picture=None,
        )

        self.mock_user_repo.find_by_google_id.assert_called_once_with(google_id)


class TestCreateJwt(AuthServiceTestCase):
    """Tests for create_jwt()."""

    def test_create_jwt_success_returns_string(self) -> None:
        """
        When: Creating JWT for valid user
        Then: Should return a string token
        """
        user = self.make_user()
        token = self.service.create_jwt(user)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_create_jwt_success_decodable(self) -> None:
        """
        When: Creating JWT
        Then: Token should be decodable
        """
        user = self.make_user()
        token = self.service.create_jwt(user)
        decoded = self.service.decode_jwt(token)
        self.assertEqual(decoded["email"], user.email)

    def test_create_jwt_success_contains_user_data(self) -> None:
        """
        When: Creating JWT
        Then: Payload should contain user info
        """
        user = self.make_user(role=UserRole.ADMIN)
        token = self.service.create_jwt(user)
        decoded = self.service.decode_jwt(token)

        self.assertEqual(decoded["sub"], str(user.id))
        self.assertEqual(decoded["email"], user.email)
        self.assertEqual(decoded["name"], user.name)
        self.assertEqual(decoded["role"], "admin")

    def test_create_jwt_success_contains_expiration(self) -> None:
        """
        When: Creating JWT
        Then: Should include exp claim
        """
        user = self.make_user()
        token = self.service.create_jwt(user)
        decoded = self.service.decode_jwt(token)
        self.assertIn("exp", decoded)
        self.assertIn("iat", decoded)

    def test_create_jwt_success_none_role(self) -> None:
        """
        When: User has no role
        Then: JWT role should be None
        """
        user = self.make_user(role=None)
        token = self.service.create_jwt(user)
        decoded = self.service.decode_jwt(token)
        self.assertIsNone(decoded["role"])


class TestDecodeJwt(AuthServiceTestCase):
    """Tests for decode_jwt()."""

    def test_decode_jwt_success_valid_token(self) -> None:
        """
        When: Valid token is decoded
        Then: Should return payload dict
        """
        user = self.make_user()
        token = self.service.create_jwt(user)
        result = self.service.decode_jwt(token)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["email"], user.email)

    def test_decode_jwt_error_invalid_token(self) -> None:
        """
        When: Invalid token string
        Then: Should raise JWTError
        """
        from jose import JWTError

        with self.assertRaises(JWTError):
            self.service.decode_jwt("invalid.token.string")

    def test_decode_jwt_error_empty_token(self) -> None:
        """
        When: Empty string token
        Then: Should raise JWTError
        """
        from jose import JWTError

        with self.assertRaises(JWTError):
            self.service.decode_jwt("")

    def test_decode_jwt_success_contains_sub(self) -> None:
        """
        When: Token is decoded
        Then: Should contain 'sub' claim
        """
        user = self.make_user()
        token = self.service.create_jwt(user)
        result = self.service.decode_jwt(token)
        self.assertIn("sub", result)

    def test_decode_jwt_success_contains_status(self) -> None:
        """
        When: Token is decoded
        Then: Should contain 'status' claim
        """
        user = self.make_user()
        token = self.service.create_jwt(user)
        result = self.service.decode_jwt(token)
        self.assertIn("status", result)
        self.assertEqual(result["status"], user.status.value)


class TestExchangeCode(AuthServiceTestCase):
    """Tests for exchange_code() async method."""

    def test_exchange_code_success(self) -> None:
        import asyncio
        from unittest.mock import AsyncMock, patch as _patch

        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": self.fake.sha256(), "token_type": "Bearer"}
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)

        with _patch("app.application.services.auth_service.httpx.AsyncClient", return_value=mock_client_instance):
            result = asyncio.run(self.service.exchange_code(self.fake.bothify("code-########")))

        self.assertIn("access_token", result)
        mock_client_instance.post.assert_called_once()

    def test_exchange_code_error_raises_on_failure(self) -> None:
        import asyncio
        from unittest.mock import AsyncMock, patch as _patch

        import httpx

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401", request=MagicMock(), response=MagicMock()
        )

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)

        with _patch("app.application.services.auth_service.httpx.AsyncClient", return_value=mock_client_instance):
            with self.assertRaises(httpx.HTTPStatusError):
                asyncio.run(self.service.exchange_code("bad-code"))


class TestGetGoogleUserInfo(AuthServiceTestCase):
    """Tests for get_google_user_info() async method."""

    def test_get_google_user_info_success(self) -> None:
        import asyncio
        from unittest.mock import AsyncMock, patch as _patch

        user_info = {
            "id": self.fake.bothify("########"),
            "email": self.fake.email(),
            "name": self.fake.name(),
            "picture": self.fake.image_url(),
        }
        mock_response = MagicMock()
        mock_response.json.return_value = user_info
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)

        with _patch("app.application.services.auth_service.httpx.AsyncClient", return_value=mock_client_instance):
            result = asyncio.run(self.service.get_google_user_info(self.fake.sha256()))

        self.assertEqual(result["email"], user_info["email"])
        mock_client_instance.get.assert_called_once()
