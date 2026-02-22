"""Tests for app.api.routes.admin – admin endpoints."""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from tests.common import BaseTestCase

from app.domain.entities.user import User, UserRole, UserStatus


def _setup_app():
    from app.api.dependencies.database import get_database
    from app.api.middleware.jwt_auth import get_current_user, require_admin
    from app.main import app

    now = datetime.utcnow()
    admin_user = User(
        id=uuid4(), google_id="g", email="admin@t.com", name="Admin",
        picture=None, role=UserRole.ADMIN, status=UserStatus.ACTIVE,
        created_at=now, updated_at=now,
    )

    app.dependency_overrides[get_database] = lambda: MagicMock()
    app.dependency_overrides[get_current_user] = lambda: admin_user
    dep_fn = require_admin()
    app.dependency_overrides[dep_fn] = lambda: admin_user

    return app, admin_user


class TestDependencyFunctions(BaseTestCase):
    """Tests for _get_repo and _get_audit_repo dependency functions."""

    def test_get_repo_success(self) -> None:
        from app.api.routes.admin import _get_repo
        from app.infrastructure.repositories.user_repository import UserRepository

        result = _get_repo(db=MagicMock())
        self.assertIsInstance(result, UserRepository)

    def test_get_audit_repo_success(self) -> None:
        from app.api.routes.admin import _get_audit_repo
        from app.infrastructure.repositories.audit_repository import AuditRepository

        result = _get_audit_repo(db=MagicMock())
        self.assertIsInstance(result, AuditRepository)


class TestListUsersRoute(BaseTestCase):
    def test_list_users_success(self) -> None:
        app, _ = _setup_app()
        from app.api.routes.admin import _get_repo

        now = datetime.utcnow()
        mock_repo = MagicMock()
        mock_user = User(
            id=uuid4(), google_id="g1", email=self.fake.email(), name=self.fake.name(),
            picture=None, role=UserRole.LOADER, status=UserStatus.ACTIVE,
            created_at=now, updated_at=now,
        )
        mock_repo.list_all.return_value = ([mock_user], 1)
        app.dependency_overrides[_get_repo] = lambda: mock_repo

        client = TestClient(app)
        resp = client.get("/api/v1/admin/users")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["total"], 1)
        app.dependency_overrides.clear()


class TestApproveUserRoute(BaseTestCase):
    def test_approve_user_success(self) -> None:
        app, _ = _setup_app()
        from app.api.routes.admin import _get_repo

        uid = uuid4()
        now = datetime.utcnow()
        mock_repo = MagicMock()
        approved = User(
            id=uid, google_id="g", email=self.fake.email(), name=self.fake.name(),
            picture=None, role=UserRole.LOADER, status=UserStatus.ACTIVE,
            created_at=now, updated_at=now,
        )
        mock_repo.approve.return_value = approved
        app.dependency_overrides[_get_repo] = lambda: mock_repo

        client = TestClient(app)
        resp = client.patch(f"/api/v1/admin/users/{uid}/approve", json={"role": "loader"})
        self.assertEqual(resp.status_code, 200)
        app.dependency_overrides.clear()

    def test_approve_user_error_not_found(self) -> None:
        app, _ = _setup_app()
        from app.api.routes.admin import _get_repo

        mock_repo = MagicMock()
        mock_repo.approve.return_value = None
        app.dependency_overrides[_get_repo] = lambda: mock_repo

        client = TestClient(app)
        resp = client.patch(f"/api/v1/admin/users/{uuid4()}/approve", json={"role": "admin"})
        self.assertEqual(resp.status_code, 404)
        app.dependency_overrides.clear()


class TestDisableUserRoute(BaseTestCase):
    def test_disable_user_success(self) -> None:
        app, _ = _setup_app()
        from app.api.routes.admin import _get_repo

        uid = uuid4()
        now = datetime.utcnow()
        mock_repo = MagicMock()
        disabled = User(
            id=uid, google_id="g", email=self.fake.email(), name=self.fake.name(),
            picture=None, role=UserRole.LOADER, status=UserStatus.DISABLED,
            created_at=now, updated_at=now,
        )
        mock_repo.disable.return_value = disabled
        app.dependency_overrides[_get_repo] = lambda: mock_repo

        client = TestClient(app)
        resp = client.patch(f"/api/v1/admin/users/{uid}/disable")
        self.assertEqual(resp.status_code, 200)
        app.dependency_overrides.clear()

    def test_disable_user_error_not_found(self) -> None:
        app, _ = _setup_app()
        from app.api.routes.admin import _get_repo

        mock_repo = MagicMock()
        mock_repo.disable.return_value = None
        app.dependency_overrides[_get_repo] = lambda: mock_repo

        client = TestClient(app)
        resp = client.patch(f"/api/v1/admin/users/{uuid4()}/disable")
        self.assertEqual(resp.status_code, 404)
        app.dependency_overrides.clear()


class TestListAuditLogsRoute(BaseTestCase):
    def test_list_audit_logs_success(self) -> None:
        app, _ = _setup_app()
        from app.api.routes.admin import _get_audit_repo

        mock_audit_repo = MagicMock()
        mock_entry = MagicMock()
        mock_entry.id = 1
        mock_entry.table_name = "documents"
        mock_entry.record_id = "42"
        mock_entry.action = "created"
        mock_entry.old_value = None
        mock_entry.new_value = "test"
        mock_entry.timestamp = datetime.utcnow()
        mock_entry.user_id = self.fake.email()
        mock_audit_repo.list_recent.return_value = ([mock_entry], 1)

        app.dependency_overrides[_get_audit_repo] = lambda: mock_audit_repo

        client = TestClient(app)
        resp = client.get("/api/v1/admin/logs")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["total"], 1)
        app.dependency_overrides.clear()
