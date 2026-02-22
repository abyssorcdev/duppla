"""Shared helpers for user integration tests."""

from unittest.mock import patch

import pytest

from faker import Faker

from app.infrastructure.repositories.user_repository import UserRepository

fake = Faker()


def create_user_in_db(db, **overrides):
    """Create a pending user via UserRepository and return the entity."""
    defaults = dict(
        google_id=fake.bothify("google-########"),
        email=fake.email(),
        name=fake.name(),
        picture=fake.image_url(),
    )
    defaults.update(overrides)
    repo = UserRepository(db)
    return repo.create(**defaults)


@pytest.fixture()
def mock_auth_settings():
    """Mock settings required by AuthService (JWT, Google OAuth)."""
    with patch("app.application.services.auth_service.settings") as mock_settings:
        mock_settings.GOOGLE_CLIENT_ID = "test-client-id"
        mock_settings.GOOGLE_REDIRECT_URI = "http://localhost:8000/auth/google/callback"
        mock_settings.GOOGLE_CLIENT_SECRET = "test-secret"  # pragma: allowlist secret
        mock_settings.JWT_SECRET_KEY = "test-jwt-secret-key-for-integration"  # pragma: allowlist secret
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_settings.JWT_EXPIRE_MINUTES = 60
        yield mock_settings
