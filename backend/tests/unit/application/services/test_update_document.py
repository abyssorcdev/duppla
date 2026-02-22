"""Tests for app.application.services.update_document.UpdateDocument."""

import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase

from app.application.dtos.document_dtos import UpdateDocumentRequest
from app.application.services.update_document import UpdateDocument
from app.domain.entities.document.document import Document
from app.domain.entities.document.status import DocumentStatus
from app.domain.exceptions import (
    DocumentNotEditableException,
    DocumentNotFoundException,
    InvalidAmountException,
)


class UpdateDocumentTestCase(BaseTestCase):
    """Global base class for ALL UpdateDocument tests."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.patcher_repo = patch(
            "app.application.services.update_document.DocumentRepository"
        )
        cls.patcher_audit = patch(
            "app.application.services.update_document.AuditRepository"
        )
        cls.MockDocumentRepository = cls.patcher_repo.start()
        cls.MockAuditRepository = cls.patcher_audit.start()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.patcher_repo.stop()
        cls.patcher_audit.stop()

    def setUp(self) -> None:
        super().setUp()
        self.mock_db = self.make_mock_db_session()
        self.mock_repo_instance = MagicMock()
        self.mock_audit_instance = MagicMock()
        self.MockDocumentRepository.return_value = self.mock_repo_instance
        self.MockAuditRepository.return_value = self.mock_audit_instance

    def tearDown(self) -> None:
        super().tearDown()
        self.MockDocumentRepository.reset_mock()
        self.MockAuditRepository.reset_mock()

    def get_instance(self) -> UpdateDocument:
        return UpdateDocument(db=self.mock_db)


class TestUnderScoreUnderScoreInit(UpdateDocumentTestCase):
    """Tests for __init__()."""

    def test_init_success_creates_repositories(self) -> None:
        """
        When: UpdateDocument is initialized
        Then: Should create both repositories
        """
        service = self.get_instance()
        self.MockDocumentRepository.assert_called_once_with(self.mock_db)
        self.MockAuditRepository.assert_called_once_with(self.mock_db)

    def test_init_success_sets_attributes(self) -> None:
        """
        When: UpdateDocument is initialized
        Then: Should have repository and audit_repository
        """
        service = self.get_instance()
        self.assertIsNotNone(service.repository)
        self.assertIsNotNone(service.audit_repository)

    def test_init_success_accepts_session(self) -> None:
        """
        When: Initialized with any session
        Then: Should not raise
        """
        service = UpdateDocument(db=MagicMock())
        self.assertIsNotNone(service)


class TestExecute(UpdateDocumentTestCase):
    """Tests for execute()."""

    def test_execute_success_update_amount(self) -> None:
        """
        When: Updating amount on a DRAFT document
        Then: Should update and return updated response
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        amount = Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True)))
        user_id = self.fake.bothify("user-####")

        existing_doc = self.make_document(id=doc_id, status=DocumentStatus.DRAFT.value)
        updated_doc = self.make_document(id=doc_id, amount=amount)

        self.mock_repo_instance.get_by_id.return_value = existing_doc
        self.mock_repo_instance.update.return_value = updated_doc

        request = UpdateDocumentRequest(
            amount=amount,
            user_id=user_id,
        )
        service = self.get_instance()
        result = service.execute(doc_id, request)

        self.assertEqual(result.id, doc_id)
        self.mock_repo_instance.update.assert_called_once()

    def test_execute_success_update_type(self) -> None:
        """
        When: Updating document type
        Then: Should update type field
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        doc_type = "receipt"
        user_id = self.fake.bothify("user-####")

        existing_doc = self.make_document(id=doc_id)
        updated_doc = self.make_document(id=doc_id, type=doc_type)

        self.mock_repo_instance.get_by_id.return_value = existing_doc
        self.mock_repo_instance.update.return_value = updated_doc

        request = UpdateDocumentRequest(type=doc_type, user_id=user_id)
        service = self.get_instance()
        result = service.execute(doc_id, request)

        self.assertEqual(result.type, doc_type)

    def test_execute_success_update_metadata(self) -> None:
        """
        When: Updating metadata
        Then: Should update metadata field
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        new_metadata = {"client": self.fake.company(), "email": self.fake.company_email()}
        user_id = self.fake.bothify("user-####")

        existing_doc = self.make_document(id=doc_id)
        updated_doc = self.make_document(id=doc_id, metadata=new_metadata)

        self.mock_repo_instance.get_by_id.return_value = existing_doc
        self.mock_repo_instance.update.return_value = updated_doc

        request = UpdateDocumentRequest(metadata=new_metadata, user_id=user_id)
        service = self.get_instance()
        result = service.execute(doc_id, request)

        self.assertEqual(result.metadata, new_metadata)

    def test_execute_success_logs_audit(self) -> None:
        """
        When: Document is updated
        Then: Should log audit entry
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        amount = Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True)))
        user_id = self.fake.bothify("user-####")

        existing_doc = self.make_document(id=doc_id)
        updated_doc = self.make_document(id=doc_id, amount=amount)

        self.mock_repo_instance.get_by_id.return_value = existing_doc
        self.mock_repo_instance.update.return_value = updated_doc

        request = UpdateDocumentRequest(amount=amount, user_id=user_id)
        service = self.get_instance()
        service.execute(doc_id, request)

        self.mock_audit_instance.log_field_updated.assert_called_once()

    def test_execute_error_document_not_found(self) -> None:
        """
        When: Document does not exist
        Then: Should raise DocumentNotFoundException
        """
        not_found_id = self.fake.random_int(min=100_000, max=999_999)
        self.mock_repo_instance.get_by_id.return_value = None

        request = UpdateDocumentRequest(
            amount=Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True))),
            user_id=self.fake.bothify("user-####"),
        )
        service = self.get_instance()

        with self.assertRaises(DocumentNotFoundException):
            service.execute(not_found_id, request)

    def test_execute_error_not_in_draft(self) -> None:
        """
        When: Document is not in DRAFT state
        Then: Should raise DocumentNotEditableException
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        existing_doc = self.make_document(id=doc_id, status=DocumentStatus.PENDING.value)
        self.mock_repo_instance.get_by_id.return_value = existing_doc

        request = UpdateDocumentRequest(
            amount=Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True))),
            user_id=self.fake.bothify("user-####"),
        )
        service = self.get_instance()

        with self.assertRaises(DocumentNotEditableException):
            service.execute(doc_id, request)

    def test_execute_error_invalid_amount(self) -> None:
        """
        When: Amount is <= 0
        Then: Pydantic DTO should reject with ValidationError
        """
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            UpdateDocumentRequest(amount=Decimal("-50.00"), user_id=self.fake.bothify("user-####"))

    def test_execute_error_approved_document(self) -> None:
        """
        When: Trying to update an APPROVED document
        Then: Should raise DocumentNotEditableException
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        existing_doc = self.make_document(id=doc_id, status=DocumentStatus.APPROVED.value)
        self.mock_repo_instance.get_by_id.return_value = existing_doc

        request = UpdateDocumentRequest(
            amount=Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True))),
            user_id=self.fake.bothify("user-####"),
        )
        service = self.get_instance()

        with self.assertRaises(DocumentNotEditableException):
            service.execute(doc_id, request)
