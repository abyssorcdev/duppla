"""Tests for app.infrastructure.notifications.tasks.celery_app – configure_logging signal."""

from unittest.mock import patch

from tests.common import BaseTestCase


class TestConfigureLogging(BaseTestCase):
    """Tests for the configure_logging signal handler."""

    def test_configure_logging_success_calls_setup(self) -> None:
        with patch("app.infrastructure.notifications.tasks.celery_app.setup_logging") as mock_setup:
            from app.infrastructure.notifications.tasks.celery_app import configure_logging

            configure_logging()
            mock_setup.assert_called_once()
