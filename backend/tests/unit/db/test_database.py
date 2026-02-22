"""Tests for app.db.database and app.infrastructure.database.session."""

from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase


class TestDbGetDb(BaseTestCase):
    """Tests for app.db.database.get_db()."""

    @patch("app.db.database.SessionLocal")
    def test_get_db_success_yields_session(self, mock_session_cls) -> None:
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        from app.db.database import get_db

        gen = get_db()
        session = next(gen)
        self.assertEqual(session, mock_session)
        try:
            next(gen)
        except StopIteration:
            pass
        mock_session.close.assert_called_once()

    @patch("app.db.database.SessionLocal")
    def test_get_db_success_closes_on_exception(self, mock_session_cls) -> None:
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        from app.db.database import get_db

        gen = get_db()
        next(gen)
        try:
            gen.throw(ValueError("test error"))
        except ValueError:
            pass
        mock_session.close.assert_called_once()


class TestDbRedisClient(BaseTestCase):
    """Tests for app.db.redis_client."""

    @patch("app.db.redis_client.redis.Redis")
    def test_get_redis_success_returns_client(self, _mock_redis) -> None:
        from app.db.redis_client import get_redis

        client = get_redis()
        self.assertIsNotNone(client)


class TestInfraGetDb(BaseTestCase):
    """Tests for app.infrastructure.database.session.get_db()."""

    @patch("app.infrastructure.database.session.SessionLocal")
    def test_get_db_success_yields_and_closes(self, mock_session_cls) -> None:
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        from app.infrastructure.database.session import get_db

        gen = get_db()
        session = next(gen)
        self.assertEqual(session, mock_session)
        try:
            next(gen)
        except StopIteration:
            pass
        mock_session.close.assert_called_once()
