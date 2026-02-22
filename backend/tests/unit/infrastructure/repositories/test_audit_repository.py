"""Tests for app.infrastructure.repositories.audit_repository.AuditRepository."""

from unittest.mock import MagicMock, call

from tests.common import BaseTestCase

from app.infrastructure.repositories.audit_repository import AuditRepository


class AuditRepositoryTestCase(BaseTestCase):
    """Base class for AuditRepository tests."""

    def setUp(self) -> None:
        super().setUp()
        self.mock_db = self.make_mock_db_session()
        self.repo = AuditRepository(self.mock_db)


class TestLog(AuditRepositoryTestCase):
    """Tests for log()."""

    def test_log_success_creates_entry(self) -> None:
        self.repo.log(
            table_name="documents",
            record_id=str(self.fake.random_int()),
            action="created",
            new_value="test",
            user_id=self.fake.email(),
        )
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()


class TestLogCreated(AuditRepositoryTestCase):
    """Tests for log_created()."""

    def test_log_created_success(self) -> None:
        self.repo.log_created("users", str(self.fake.uuid4()), "email=test@test.com", user_id="system")
        self.mock_db.add.assert_called_once()


class TestLogStateChange(AuditRepositoryTestCase):
    """Tests for log_state_change()."""

    def test_log_state_change_success(self) -> None:
        self.repo.log_state_change("documents", "1", "draft", "pending", user_id=self.fake.email())
        self.mock_db.add.assert_called_once()


class TestLogFieldUpdated(AuditRepositoryTestCase):
    """Tests for log_field_updated()."""

    def test_log_field_updated_success(self) -> None:
        self.repo.log_field_updated("users", str(self.fake.uuid4()), "role: none", "role: admin")
        self.mock_db.add.assert_called_once()


class TestListRecent(AuditRepositoryTestCase):
    """Tests for list_recent()."""

    def test_list_recent_success_no_filters(self) -> None:
        mock_query = MagicMock()
        mock_query.count.return_value = 2
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [MagicMock(), MagicMock()]
        self.mock_db.query.return_value = mock_query

        entries, total = self.repo.list_recent()
        self.assertEqual(total, 2)
        self.assertEqual(len(entries), 2)

    def test_list_recent_success_with_action_filter(self) -> None:
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        mock_filtered.count.return_value = 1
        mock_filtered.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [MagicMock()]
        self.mock_db.query.return_value = mock_query

        entries, total = self.repo.list_recent(action="created")
        self.assertEqual(total, 1)

    def test_list_recent_success_with_table_filter(self) -> None:
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        mock_filtered.count.return_value = 0
        mock_filtered.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query

        entries, total = self.repo.list_recent(table_name="jobs")
        self.assertEqual(total, 0)

    def test_list_recent_success_with_both_filters(self) -> None:
        mock_query = MagicMock()
        mock_filtered1 = MagicMock()
        mock_filtered2 = MagicMock()
        mock_query.filter.return_value = mock_filtered1
        mock_filtered1.filter.return_value = mock_filtered2
        mock_filtered2.count.return_value = 3
        mock_filtered2.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            MagicMock() for _ in range(3)
        ]
        self.mock_db.query.return_value = mock_query

        entries, total = self.repo.list_recent(action="state_change", table_name="documents")
        self.assertEqual(total, 3)

    def test_list_recent_success_pagination(self) -> None:
        mock_query = MagicMock()
        mock_query.count.return_value = 100
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [MagicMock()]
        self.mock_db.query.return_value = mock_query

        entries, total = self.repo.list_recent(skip=10, limit=1)
        self.assertEqual(total, 100)
        self.assertEqual(len(entries), 1)
