"""Tests for app.api.routes.jobs – endpoints via TestClient."""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from tests.common import BaseTestCase

from app.domain.entities.user import User, UserRole, UserStatus


def _make_user():
    now = datetime.utcnow()
    return User(
        id=uuid4(), google_id="g", email="u@t.com", name="T",
        picture=None, role=UserRole.ADMIN, status=UserStatus.ACTIVE,
        created_at=now, updated_at=now,
    )


class TestListJobsRoute(BaseTestCase):
    def test_list_jobs_success(self) -> None:
        from app.api.dependencies.database import get_database
        from app.api.dependencies.services import get_list_jobs_service
        from app.api.middleware.jwt_auth import get_current_user, require_any_active_role
        from app.main import app

        user = _make_user()
        mock_svc = MagicMock()
        mock_svc.execute.return_value = MagicMock(
            items=[], total=0, page=1, page_size=10, total_pages=0,
        )

        app.dependency_overrides[get_database] = lambda: MagicMock()
        app.dependency_overrides[get_current_user] = lambda: user
        dep_fn = require_any_active_role()
        app.dependency_overrides[dep_fn] = lambda: user
        app.dependency_overrides[get_list_jobs_service] = lambda: mock_svc

        client = TestClient(app)
        resp = client.get("/api/v1/jobs")
        self.assertEqual(resp.status_code, 200)
        app.dependency_overrides.clear()


class TestGetJobStatusRoute(BaseTestCase):
    def test_get_job_status_success(self) -> None:
        from app.api.dependencies.database import get_database
        from app.api.dependencies.services import get_get_job_status_service
        from app.api.middleware.jwt_auth import get_current_user, require_any_active_role
        from app.main import app

        user = _make_user()
        job_id = uuid4()
        mock_svc = MagicMock()
        mock_svc.execute.return_value = MagicMock(
            job_id=job_id, status="completed", created_at=self.test_timestamp,
            completed_at=self.test_timestamp, result={"processed": 1}, error_message=None,
        )

        app.dependency_overrides[get_database] = lambda: MagicMock()
        app.dependency_overrides[get_current_user] = lambda: user
        dep_fn = require_any_active_role()
        app.dependency_overrides[dep_fn] = lambda: user
        app.dependency_overrides[get_get_job_status_service] = lambda: mock_svc

        client = TestClient(app)
        resp = client.get(f"/api/v1/jobs/{job_id}")
        self.assertEqual(resp.status_code, 200)
        app.dependency_overrides.clear()
