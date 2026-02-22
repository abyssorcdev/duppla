"""Tests for app.core.config – property branches and API_KEYS_ALLOWED."""

import os
from unittest.mock import patch

from fastapi import HTTPException

from tests.common import BaseTestCase

from app.core.config import Settings


class TestDatabaseUrlProperty(BaseTestCase):
    """Tests for Settings.DATABASE_URL property."""

    def test_database_url_from_env(self) -> None:
        expected = "postgresql://remote:pass@host:5432/mydb"  # pragma: allowlist secret
        with patch.dict(os.environ, {"DATABASE_URL": expected}):
            s = Settings()
            self.assertEqual(s.DATABASE_URL, expected)

    def test_database_url_built_from_components(self) -> None:
        env_clean = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
        with patch.dict(os.environ, env_clean, clear=True):
            s = Settings()
            self.assertIn(s.POSTGRES_USER, s.DATABASE_URL)
            self.assertIn(s.POSTGRES_HOST, s.DATABASE_URL)


class TestRedisUrlProperty(BaseTestCase):
    """Tests for Settings.REDIS_URL property."""

    def test_redis_url_from_env(self) -> None:
        expected = "redis://remote-redis:6380/1"
        with patch.dict(os.environ, {"REDIS_URL": expected}):
            s = Settings()
            self.assertEqual(s.REDIS_URL, expected)

    def test_redis_url_built_from_components(self) -> None:
        env_clean = {k: v for k, v in os.environ.items() if k != "REDIS_URL"}
        with patch.dict(os.environ, env_clean, clear=True):
            s = Settings()
            self.assertIn("redis://", s.REDIS_URL)


class TestApiKeysAllowed(BaseTestCase):
    """Tests for Settings.API_KEYS_ALLOWED."""

    def test_api_keys_allowed_success_get(self) -> None:
        s = Settings()
        keys = s.API_KEYS_ALLOWED("GET")
        self.assertIsInstance(keys, list)
        self.assertTrue(len(keys) > 0)

    def test_api_keys_allowed_success_post(self) -> None:
        s = Settings()
        keys = s.API_KEYS_ALLOWED("POST")
        self.assertIsInstance(keys, list)

    def test_api_keys_allowed_error_unknown_method(self) -> None:
        s = Settings()
        with self.assertRaises(HTTPException) as ctx:
            s.API_KEYS_ALLOWED("OPTIONS")
        self.assertEqual(ctx.exception.status_code, 401)
