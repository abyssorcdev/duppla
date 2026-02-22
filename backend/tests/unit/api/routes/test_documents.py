"""Tests for app.api.routes.documents – endpoints via TestClient."""

from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from tests.common import BaseTestCase

from app.domain.entities.user import User, UserRole, UserStatus


def _make_app():
    from app.api.dependencies.database import get_database
    from app.api.middleware.jwt_auth import get_current_user, require_any_active_role, require_approver, require_loader
    from app.main import app

    mock_db = MagicMock()
    now = datetime.utcnow()

    active_user = User(
        id=uuid4(), google_id="g1", email="user@test.com", name="Test",
        picture=None, role=UserRole.ADMIN, status=UserStatus.ACTIVE,
        created_at=now, updated_at=now,
    )

    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: active_user

    for dep_factory in [require_any_active_role, require_loader, require_approver]:
        dep_fn = dep_factory()
        app.dependency_overrides[dep_fn] = lambda: active_user

    return app, mock_db


class TestCreateDocumentRoute(BaseTestCase):
    def test_create_document_success(self) -> None:
        app, _ = _make_app()
        from app.api.dependencies.services import get_create_document_service

        mock_svc = MagicMock()
        mock_svc.execute.return_value = MagicMock(
            id=1, type="invoice", amount=Decimal("100.00"), status="draft",
            created_at=self.test_timestamp, updated_at=self.test_timestamp,
            metadata={}, created_by="user",
        )
        app.dependency_overrides[get_create_document_service] = lambda: mock_svc

        client = TestClient(app)
        resp = client.post("/api/v1/documents", json={"type": "invoice", "amount": 100.00, "metadata": {}})
        self.assertEqual(resp.status_code, 201)
        app.dependency_overrides.clear()


class TestGetDocumentRoute(BaseTestCase):
    def test_get_document_success(self) -> None:
        app, _ = _make_app()
        from app.api.dependencies.services import get_get_document_service

        mock_svc = MagicMock()
        mock_svc.execute.return_value = MagicMock(
            id=1, type="invoice", amount=Decimal("100.00"), status="draft",
            created_at=self.test_timestamp, updated_at=self.test_timestamp,
            metadata={}, created_by="user",
        )
        app.dependency_overrides[get_get_document_service] = lambda: mock_svc

        client = TestClient(app)
        resp = client.get("/api/v1/documents/1")
        self.assertEqual(resp.status_code, 200)
        app.dependency_overrides.clear()


class TestUpdateDocumentRoute(BaseTestCase):
    def test_update_document_success(self) -> None:
        app, _ = _make_app()
        from app.api.dependencies.services import get_update_document_service

        mock_svc = MagicMock()
        mock_svc.execute.return_value = MagicMock(
            id=1, type="receipt", amount=Decimal("200.00"), status="draft",
            created_at=self.test_timestamp, updated_at=self.test_timestamp,
            metadata={}, created_by="user",
        )
        app.dependency_overrides[get_update_document_service] = lambda: mock_svc

        client = TestClient(app)
        resp = client.put("/api/v1/documents/1", json={"amount": 200.00, "user_id": "usr"})
        self.assertEqual(resp.status_code, 200)
        app.dependency_overrides.clear()


class TestUpdateStatusRoute(BaseTestCase):
    def test_update_status_success(self) -> None:
        app, _ = _make_app()
        from app.api.dependencies.services import get_update_status_service

        mock_svc = MagicMock()
        mock_svc.execute.return_value = MagicMock(
            id=1, type="invoice", amount=Decimal("100.00"), status="pending",
            created_at=self.test_timestamp, updated_at=self.test_timestamp,
            metadata={}, created_by="user",
        )
        app.dependency_overrides[get_update_status_service] = lambda: mock_svc

        client = TestClient(app)
        resp = client.patch("/api/v1/documents/1/status", json={"new_status": "pending"})
        self.assertEqual(resp.status_code, 200)
        app.dependency_overrides.clear()


class TestSearchDocumentsRoute(BaseTestCase):
    def test_search_documents_success(self) -> None:
        app, _ = _make_app()
        from app.api.dependencies.services import get_search_documents_service

        mock_svc = MagicMock()
        mock_svc.execute.return_value = MagicMock(
            items=[], total=0, page=1, page_size=50, total_pages=0,
        )
        app.dependency_overrides[get_search_documents_service] = lambda: mock_svc

        client = TestClient(app)
        resp = client.get("/api/v1/documents")
        self.assertEqual(resp.status_code, 200)
        app.dependency_overrides.clear()
