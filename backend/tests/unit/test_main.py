"""Tests for app.main – FastAPI app and health endpoints."""

from fastapi.testclient import TestClient

from tests.common import BaseTestCase

from app.main import app


class TestRootEndpoint(BaseTestCase):
    """Tests for GET /."""

    def test_root_success_returns_info(self) -> None:
        client = TestClient(app)
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("message", data)
        self.assertIn("version", data)
        self.assertIn("docs", data)


class TestHealthEndpoint(BaseTestCase):
    """Tests for GET /health."""

    def test_health_success_returns_healthy(self) -> None:
        client = TestClient(app)
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "healthy")


class TestAppConfiguration(BaseTestCase):
    """Tests for app configuration."""

    def test_app_has_title(self) -> None:
        self.assertIsNotNone(app.title)

    def test_app_has_version(self) -> None:
        self.assertIsNotNone(app.version)

    def test_app_includes_routes(self) -> None:
        route_paths = [r.path for r in app.routes]
        self.assertIn("/", route_paths)
        self.assertIn("/health", route_paths)
