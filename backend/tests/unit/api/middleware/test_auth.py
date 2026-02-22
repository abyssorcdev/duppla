"""Tests for app.api.middleware.auth.verify_api_key."""

import asyncio
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from tests.common import BaseTestCase


class TestVerifyApiKey(BaseTestCase):
    """Tests for verify_api_key()."""

    def _run(self, request, api_key):
        from app.api.middleware.auth import verify_api_key

        return asyncio.run(verify_api_key(request, api_key))

    def test_verify_api_key_error_missing_key(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            self._run(MagicMock(), None)
        self.assertEqual(ctx.exception.status_code, 401)

    @patch("app.api.middleware.auth._redis")
    def test_verify_api_key_success_cached_valid(self, mock_redis) -> None:
        mock_redis.is_key_cached_valid.return_value = True
        mock_redis.check_rate_limit.return_value = (True, 1, 0)

        request = MagicMock()
        request.method = "GET"
        result = self._run(request, "get-key-123")
        self.assertEqual(result, "get-key-123")

    @patch("app.api.middleware.auth._redis")
    def test_verify_api_key_success_not_cached_valid_key(self, mock_redis) -> None:
        mock_redis.is_key_cached_valid.return_value = False
        mock_redis.check_rate_limit.return_value = (True, 1, 0)

        request = MagicMock()
        request.method = "GET"
        result = self._run(request, "get-key-123")
        self.assertEqual(result, "get-key-123")
        mock_redis.cache_valid_key.assert_called_once()

    @patch("app.api.middleware.auth._redis")
    def test_verify_api_key_error_invalid_key(self, mock_redis) -> None:
        mock_redis.is_key_cached_valid.return_value = False

        request = MagicMock()
        request.method = "GET"
        with self.assertRaises(HTTPException) as ctx:
            self._run(request, "bad-key")
        self.assertEqual(ctx.exception.status_code, 401)

    @patch("app.api.middleware.auth._redis")
    def test_verify_api_key_error_rate_limited(self, mock_redis) -> None:
        mock_redis.is_key_cached_valid.return_value = True
        mock_redis.check_rate_limit.return_value = (False, 101, 30)

        request = MagicMock()
        request.method = "GET"
        with self.assertRaises(HTTPException) as ctx:
            self._run(request, "get-key-123")
        self.assertEqual(ctx.exception.status_code, 429)

    @patch("app.api.middleware.auth._redis")
    def test_verify_api_key_success_redis_down_fallback(self, mock_redis) -> None:
        mock_redis.is_key_cached_valid.side_effect = ConnectionError("redis down")

        request = MagicMock()
        request.method = "GET"
        result = self._run(request, "get-key-123")
        self.assertEqual(result, "get-key-123")

    @patch("app.api.middleware.auth._redis")
    def test_verify_api_key_error_redis_down_invalid_key(self, mock_redis) -> None:
        mock_redis.is_key_cached_valid.side_effect = ConnectionError("redis down")

        request = MagicMock()
        request.method = "GET"
        with self.assertRaises(HTTPException) as ctx:
            self._run(request, "wrong-key")
        self.assertEqual(ctx.exception.status_code, 401)
