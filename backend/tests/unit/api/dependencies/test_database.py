"""Tests for app.api.dependencies.database.get_database."""

from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase


class TestGetDatabase(BaseTestCase):
    """Tests for get_database()."""

    @patch("app.api.dependencies.database.get_db")
    def test_get_database_success_yields_from_get_db(self, mock_get_db) -> None:
        mock_session = MagicMock()
        mock_get_db.return_value = iter([mock_session])

        from app.api.dependencies.database import get_database

        gen = get_database()
        session = next(gen)
        self.assertEqual(session, mock_session)
