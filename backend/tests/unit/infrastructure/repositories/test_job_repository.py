"""Tests for app.infrastructure.repositories.job_repository.JobRepository – coverage gaps."""

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

from tests.common import BaseTestCase

from app.domain.exceptions import JobNotFoundException


class JobRepositoryTestCase(BaseTestCase):
    """Base class for JobRepository tests."""

    def setUp(self) -> None:
        super().setUp()
        self.mock_db = self.make_mock_db_session()
        with patch("app.infrastructure.repositories.job_repository._SKIP_AUDIT_SQL"):
            from app.infrastructure.repositories.job_repository import JobRepository

            self.repo = JobRepository(self.mock_db)

    def _make_db_model(self, **overrides):
        model = MagicMock()
        model.id = overrides.get("id", uuid4())
        model.document_ids = overrides.get("document_ids", [1, 2, 3])
        model.status = overrides.get("status", "pending")
        model.created_at = datetime.utcnow()
        model.completed_at = overrides.get("completed_at", None)
        model.error_message = overrides.get("error_message", None)
        model.result = overrides.get("result", None)
        return model


class TestCreate(JobRepositoryTestCase):
    """Tests for create()."""

    def test_create_success(self) -> None:
        job = self.make_job()
        self.repo.create(job)
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()


class TestGetById(JobRepositoryTestCase):
    """Tests for get_by_id()."""

    def test_get_by_id_success_found(self) -> None:
        db_model = self._make_db_model()
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model
        result = self.repo.get_by_id(db_model.id)
        self.assertIsNotNone(result)

    def test_get_by_id_success_not_found(self) -> None:
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = self.repo.get_by_id(uuid4())
        self.assertIsNone(result)


class TestListAll(JobRepositoryTestCase):
    """Tests for list_all()."""

    def test_list_all_success_no_filter(self) -> None:
        mock_query = MagicMock()
        mock_query.count.return_value = 2
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            self._make_db_model(), self._make_db_model()
        ]
        self.mock_db.query.return_value = mock_query
        jobs, total = self.repo.list_all()
        self.assertEqual(total, 2)

    def test_list_all_success_with_status_filter(self) -> None:
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        mock_filtered.count.return_value = 1
        mock_filtered.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [self._make_db_model()]
        self.mock_db.query.return_value = mock_query
        jobs, total = self.repo.list_all(status="completed")
        self.assertEqual(total, 1)


class TestUpdateStatus(JobRepositoryTestCase):
    """Tests for update_status()."""

    def test_update_status_success(self) -> None:
        db_model = self._make_db_model()
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model
        result = self.repo.update_status(db_model.id, "completed", result={"processed": 5})
        self.mock_db.commit.assert_called()

    def test_update_status_success_with_all_kwargs(self) -> None:
        db_model = self._make_db_model()
        self.mock_db.query.return_value.filter.return_value.first.return_value = db_model
        now = datetime.utcnow()
        result = self.repo.update_status(
            db_model.id, "failed",
            completed_at=now,
            error_message="err",
            result={"failed": 1},
        )
        self.mock_db.commit.assert_called()

    def test_update_status_error_not_found(self) -> None:
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(JobNotFoundException):
            self.repo.update_status(uuid4(), "completed")
