"""Base test case for the entire Duppla backend project.

Provides shared helpers, Faker-powered factories, and test data generators
used across all unit and integration tests.
"""

import unittest
from decimal import Decimal
from typing import Any, Dict
from unittest.mock import MagicMock

from faker import Faker

from app.domain.entities.document.document import Document
from app.domain.entities.document.status import DocumentStatus
from app.domain.entities.job.job import Job
from app.domain.entities.job.status import JobStatus
from app.domain.entities.user import User, UserRole, UserStatus


class BaseTestCase(unittest.TestCase):
    """Base test case with shared utilities for all Duppla tests."""

    fake = Faker()

    def setUp(self) -> None:
        super().setUp()
        self.setup_common_test_data()

    def setup_common_test_data(self) -> None:
        self.test_user_id = self.fake.bothify("user-####-??")
        self.test_user_email = self.fake.email()
        self.test_timestamp = self.fake.date_time_between(start_date="-2y", end_date="now")
        self.test_uuid = self.fake.uuid4(cast_to=None)

    # ── Document Factories ────────────────────────────────────────────────────

    def make_document(self, **overrides: Any) -> Document:
        defaults: Dict[str, Any] = {
            "type": self.fake.random_element(["invoice", "receipt", "voucher"]),
            "amount": Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True))),
            "metadata": {"client": self.fake.company(), "email": self.fake.company_email()},
            "id": self.fake.random_int(min=1, max=99_999),
            "status": DocumentStatus.DRAFT.value,
            "created_at": self.test_timestamp,
            "updated_at": self.test_timestamp,
            "created_by": self.test_user_id,
        }
        defaults.update(overrides)
        return Document(**defaults)

    def make_document_response_data(self, **overrides: Any) -> Dict[str, Any]:
        defaults: Dict[str, Any] = {
            "id": self.fake.random_int(min=1, max=99_999),
            "type": self.fake.random_element(["invoice", "receipt", "voucher"]),
            "amount": Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True))),
            "status": DocumentStatus.DRAFT.value,
            "created_at": self.test_timestamp,
            "updated_at": self.test_timestamp,
            "metadata": {"client": self.fake.company(), "email": self.fake.company_email()},
            "created_by": self.test_user_id,
        }
        defaults.update(overrides)
        return defaults

    # ── Job Factories ─────────────────────────────────────────────────────────

    def make_job(self, **overrides: Any) -> Job:
        defaults: Dict[str, Any] = {
            "document_ids": [self.fake.random_int(min=1, max=999) for _ in range(3)],
            "id": self.test_uuid,
            "status": JobStatus.PENDING.value,
            "created_at": self.test_timestamp,
        }
        defaults.update(overrides)
        return Job(**defaults)

    # ── User Factories ────────────────────────────────────────────────────────

    def make_user(self, **overrides: Any) -> User:
        defaults: Dict[str, Any] = {
            "id": self.test_uuid,
            "google_id": self.fake.bothify("google-########"),
            "email": self.test_user_email,
            "name": self.fake.name(),
            "picture": self.fake.image_url(),
            "role": UserRole.LOADER,
            "status": UserStatus.ACTIVE,
            "created_at": self.test_timestamp,
            "updated_at": self.test_timestamp,
        }
        defaults.update(overrides)
        return User(**defaults)

    # ── Mock Factories ────────────────────────────────────────────────────────

    def make_mock_db_session(self) -> MagicMock:
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_db.execute = MagicMock()
        mock_db.query = MagicMock()
        return mock_db

    def make_mock_repository(self) -> MagicMock:
        return MagicMock()
