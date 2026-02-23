"""Tests for app.infrastructure.database.session."""

from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase


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
