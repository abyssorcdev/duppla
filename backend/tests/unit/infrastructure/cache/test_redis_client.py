"""Tests for app.infrastructure.cache.redis_client.RedisClient."""

from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase


class RedisClientTestCase(BaseTestCase):
    """Base class for RedisClient tests."""

    def setUp(self) -> None:
        super().setUp()
        self.mock_redis = MagicMock()
        with patch(
            "app.infrastructure.cache.redis_client.redis.from_url",
            return_value=self.mock_redis,
        ):
            from app.infrastructure.cache.redis_client import RedisClient

            self.client = RedisClient()


class TestIsKeyCachedValid(RedisClientTestCase):
    """Tests for is_key_cached_valid()."""

    def test_is_key_cached_valid_success_exists(self) -> None:
        self.mock_redis.exists.return_value = 1
        key = self.fake.sha256()
        self.assertTrue(self.client.is_key_cached_valid(key))

    def test_is_key_cached_valid_success_not_exists(self) -> None:
        self.mock_redis.exists.return_value = 0
        self.assertFalse(self.client.is_key_cached_valid(self.fake.sha256()))


class TestCacheValidKey(RedisClientTestCase):
    """Tests for cache_valid_key()."""

    def test_cache_valid_key_success_calls_setex(self) -> None:
        key = self.fake.sha256()
        self.client.cache_valid_key(key)
        self.mock_redis.setex.assert_called_once()


class TestInvalidateKey(RedisClientTestCase):
    """Tests for invalidate_key()."""

    def test_invalidate_key_success_calls_delete(self) -> None:
        key = self.fake.sha256()
        self.client.invalidate_key(key)
        self.mock_redis.delete.assert_called_once()


class TestCheckRateLimit(RedisClientTestCase):
    """Tests for check_rate_limit()."""

    def test_check_rate_limit_success_first_request(self) -> None:
        self.mock_redis.incr.return_value = 1
        allowed, count, retry = self.client.check_rate_limit("key1")
        self.assertTrue(allowed)
        self.assertEqual(count, 1)
        self.assertEqual(retry, 0)
        self.mock_redis.expire.assert_called_once()

    def test_check_rate_limit_success_within_limit(self) -> None:
        self.mock_redis.incr.return_value = 50
        allowed, count, retry = self.client.check_rate_limit("key1")
        self.assertTrue(allowed)
        self.assertEqual(count, 50)

    def test_check_rate_limit_error_exceeded(self) -> None:
        self.mock_redis.incr.return_value = 101
        self.mock_redis.ttl.return_value = 30
        allowed, count, retry = self.client.check_rate_limit("key1")
        self.assertFalse(allowed)
        self.assertEqual(retry, 30)

    def test_check_rate_limit_error_exceeded_ttl_zero(self) -> None:
        self.mock_redis.incr.return_value = 200
        self.mock_redis.ttl.return_value = 0
        allowed, _, retry = self.client.check_rate_limit("key1")
        self.assertFalse(allowed)
        self.assertEqual(retry, 1)
