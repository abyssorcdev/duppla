"""Tests for app.infrastructure.database.models.job.JobModel.to_dict."""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from tests.common import BaseTestCase


class TestJobModelToDict(BaseTestCase):
    """Tests for JobModel.to_dict()."""

    def _make_model(self) -> MagicMock:
        model = MagicMock()
        model.id = uuid4()
        model.document_ids = [self.fake.random_int() for _ in range(3)]
        model.status = "pending"
        model.created_at = datetime.utcnow()
        model.completed_at = None
        model.error_message = None
        model.result = None
        return model

    def test_to_dict_success_returns_all_keys(self) -> None:
        from app.infrastructure.database.models.job import JobModel

        model = self._make_model()
        result = JobModel.to_dict(model)
        expected_keys = {"id", "document_ids", "status", "created_at", "completed_at", "error_message", "result"}
        self.assertEqual(set(result.keys()), expected_keys)

    def test_to_dict_success_completed_job(self) -> None:
        from app.infrastructure.database.models.job import JobModel

        model = self._make_model()
        model.status = "completed"
        model.completed_at = datetime.utcnow()
        model.result = {"processed": self.fake.random_int(min=1, max=10)}
        result = JobModel.to_dict(model)
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["completed_at"])
        self.assertIsNotNone(result["result"])
