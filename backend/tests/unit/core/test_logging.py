"""Tests for app.core.logging.setup_logging."""

import logging

from tests.common import BaseTestCase

from app.core.logging import setup_logging


class TestSetupLogging(BaseTestCase):
    """Tests for setup_logging()."""

    def test_setup_logging_success_default_level(self) -> None:
        setup_logging()
        root = logging.getLogger()
        self.assertEqual(root.level, logging.INFO)

    def test_setup_logging_success_debug_level(self) -> None:
        setup_logging("DEBUG")
        root = logging.getLogger()
        self.assertEqual(root.level, logging.DEBUG)

    def test_setup_logging_success_warning_level(self) -> None:
        setup_logging("WARNING")
        root = logging.getLogger()
        self.assertEqual(root.level, logging.WARNING)

    def test_setup_logging_success_sets_third_party_loggers(self) -> None:
        setup_logging("DEBUG")
        self.assertEqual(logging.getLogger("uvicorn.error").level, logging.INFO)
        self.assertEqual(logging.getLogger("uvicorn.access").level, logging.INFO)
        self.assertEqual(logging.getLogger("httpx").level, logging.WARNING)
        self.assertEqual(logging.getLogger("sqlalchemy.engine").level, logging.WARNING)

    def test_setup_logging_success_invalid_level_falls_back(self) -> None:
        setup_logging("INVALID_LEVEL")
        root = logging.getLogger()
        self.assertEqual(root.level, logging.INFO)
