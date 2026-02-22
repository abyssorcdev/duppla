"""Tests for app.api.routes.batch – process batch endpoint."""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from tests.common import BaseTestCase

from app.domain.entities.user import User, UserRole, UserStatus


class TestProcessBatchRoute(BaseTestCase):
    def test_process_batch_success(self) -> None:
        from app.api.dependencies.database import get_database
        from app.api.dependencies.services import get_process_batch_service
        from app.api.middleware.jwt_auth import get_current_user, require_loader
        from app.main import app

        now = datetime.utcnow()
        user = User(
            id=uuid4(), google_id="g", email="u@t.com", name="T",
            picture=None, role=UserRole.LOADER, status=UserStatus.ACTIVE,
            created_at=now, updated_at=now,
        )
        mock_svc = MagicMock()
        mock_svc.execute.return_value = MagicMock(
            job_id=uuid4(), status="pending", created_at=self.test_timestamp,
            completed_at=None, result=None, error_message=None,
        )

        app.dependency_overrides[get_database] = lambda: MagicMock()
        app.dependency_overrides[get_current_user] = lambda: user
        dep_fn = require_loader()
        app.dependency_overrides[dep_fn] = lambda: user
        app.dependency_overrides[get_process_batch_service] = lambda: mock_svc

        client = TestClient(app)
        resp = client.post("/api/v1/documents/batch/process", json={"document_ids": [1, 2, 3]})
        self.assertEqual(resp.status_code, 202)
        app.dependency_overrides.clear()
