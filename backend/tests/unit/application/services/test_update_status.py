"""Tests for app.application.services.update_status.UpdateStatus."""

import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase

from app.application.dtos.document_dtos import UpdateStatusRequest
from app.application.services.update_status import UpdateStatus
from app.domain.entities.document.document import Document
from app.domain.entities.document.status import DocumentStatus
from app.domain.exceptions import (
    DocumentNotFoundException,
    InvalidStateTransitionException,
)


class UpdateStatusTestCase(BaseTestCase):
    """Global base class for ALL UpdateStatus tests."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.patcher_doc_repo = patch(
            "app.application.services.update_status.DocumentRepository"
        )
        cls.patcher_audit_repo = patch(
            "app.application.services.update_status.AuditRepository"
        )
        cls.MockDocumentRepository = cls.patcher_doc_repo.start()
        cls.MockAuditRepository = cls.patcher_audit_repo.start()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.patcher_doc_repo.stop()
        cls.patcher_audit_repo.stop()

    def setUp(self) -> None:
        super().setUp()
        self.mock_db = self.make_mock_db_session()
        self.mock_doc_repo = MagicMock()
        self.mock_audit_repo = MagicMock()
        self.MockDocumentRepository.return_value = self.mock_doc_repo
        self.MockAuditRepository.return_value = self.mock_audit_repo

    def tearDown(self) -> None:
        super().tearDown()
        self.MockDocumentRepository.reset_mock()
        self.MockAuditRepository.reset_mock()

    def get_instance(self) -> UpdateStatus:
        return UpdateStatus(db=self.mock_db)


class TestUnderScoreUnderScoreInit(UpdateStatusTestCase):
    """Tests for __init__()."""

    def test_init_success_creates_repositories(self) -> None:
        """
        When: UpdateStatus is initialized
        Then: Should create both repositories
        """
        service = self.get_instance()
        self.MockDocumentRepository.assert_called_once_with(self.mock_db)
        self.MockAuditRepository.assert_called_once_with(self.mock_db)

    def test_init_success_sets_attributes(self) -> None:
        """
        When: UpdateStatus is initialized
        Then: Should set document_repository and audit_repository
        """
        service = self.get_instance()
        self.assertIsNotNone(service.document_repository)
        self.assertIsNotNone(service.audit_repository)

    def test_init_success_accepts_session(self) -> None:
        """
        When: Initialized with any session
        Then: Should not raise
        """
        service = UpdateStatus(db=MagicMock())
        self.assertIsNotNone(service)


class TestExecute(UpdateStatusTestCase):
    """Tests for execute()."""

    def test_execute_success_draft_to_pending(self) -> None:
        """
        When: Transitioning from DRAFT to PENDING
        Then: Should update status and return response
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        user_email = self.fake.email()

        existing_doc = self.make_document(id=doc_id, status=DocumentStatus.DRAFT.value)
        updated_doc = self.make_document(id=doc_id, status=DocumentStatus.PENDING.value)

        self.mock_doc_repo.get_by_id.return_value = existing_doc
        self.mock_doc_repo.update.return_value = updated_doc

        request = UpdateStatusRequest(new_status=DocumentStatus.PENDING)
        service = self.get_instance()
        result = service.execute(doc_id, request, user_email)

        self.assertEqual(result.status, DocumentStatus.PENDING.value)

    def test_execute_success_pending_to_approved(self) -> None:
        """
        When: Transitioning from PENDING to APPROVED
        Then: Should update status successfully
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        approver_email = self.fake.email()

        existing_doc = self.make_document(id=doc_id, status=DocumentStatus.PENDING.value)
        updated_doc = self.make_document(id=doc_id, status=DocumentStatus.APPROVED.value)

        self.mock_doc_repo.get_by_id.return_value = existing_doc
        self.mock_doc_repo.update.return_value = updated_doc

        request = UpdateStatusRequest(new_status=DocumentStatus.APPROVED)
        service = self.get_instance()
        result = service.execute(doc_id, request, approver_email)

        self.assertEqual(result.status, DocumentStatus.APPROVED.value)

    def test_execute_success_pending_to_rejected_with_comment(self) -> None:
        """
        When: Rejecting with a comment
        Then: Should enrich metadata with rejection info
        """
        existing_doc = self.make_document(
            id=3, status=DocumentStatus.PENDING.value, metadata={"client": "Acme"},
        )
        updated_doc = self.make_document(id=3, status=DocumentStatus.REJECTED.value)

        self.mock_doc_repo.get_by_id.return_value = existing_doc
        self.mock_doc_repo.update.return_value = updated_doc

        request = UpdateStatusRequest(
            new_status=DocumentStatus.REJECTED,
            comment="Missing attachments",
        )
        service = self.get_instance()
        result = service.execute(3, request, "reviewer@duppla.test")

        update_call_args = self.mock_doc_repo.update.call_args
        update_data = update_call_args[0][1]
        self.assertIn("metadata", update_data)
        self.assertEqual(update_data["metadata"]["rejection_comment"], "Missing attachments")
        self.assertEqual(update_data["metadata"]["rejected_by"], "reviewer@duppla.test")

    def test_execute_success_logs_audit(self) -> None:
        """
        When: Status is updated
        Then: Should log state change audit
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        user_email = self.fake.email()

        existing_doc = self.make_document(id=doc_id, status=DocumentStatus.DRAFT.value)
        updated_doc = self.make_document(id=doc_id, status=DocumentStatus.PENDING.value)

        self.mock_doc_repo.get_by_id.return_value = existing_doc
        self.mock_doc_repo.update.return_value = updated_doc

        request = UpdateStatusRequest(new_status=DocumentStatus.PENDING)
        service = self.get_instance()
        service.execute(doc_id, request, user_email)

        self.mock_audit_repo.log_state_change.assert_called_once()

    def test_execute_success_rejection_without_comment(self) -> None:
        """
        When: Rejecting without a comment
        Then: Should not enrich metadata with rejection info
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        user_email = self.fake.email()

        existing_doc = self.make_document(id=doc_id, status=DocumentStatus.PENDING.value)
        updated_doc = self.make_document(id=doc_id, status=DocumentStatus.REJECTED.value)

        self.mock_doc_repo.get_by_id.return_value = existing_doc
        self.mock_doc_repo.update.return_value = updated_doc

        request = UpdateStatusRequest(new_status=DocumentStatus.REJECTED)
        service = self.get_instance()
        service.execute(doc_id, request, user_email)

        update_call_args = self.mock_doc_repo.update.call_args
        update_data = update_call_args[0][1]
        self.assertNotIn("metadata", update_data)

    def test_execute_error_document_not_found(self) -> None:
        """
        When: Document does not exist
        Then: Should raise DocumentNotFoundException
        """
        not_found_id = self.fake.random_int(min=100_000, max=999_999)
        self.mock_doc_repo.get_by_id.return_value = None

        request = UpdateStatusRequest(new_status=DocumentStatus.PENDING)
        service = self.get_instance()

        with self.assertRaises(DocumentNotFoundException):
            service.execute(not_found_id, request, self.fake.email())

    def test_execute_error_invalid_transition(self) -> None:
        """
        When: Transition is not allowed (e.g., DRAFT -> APPROVED)
        Then: Should raise InvalidStateTransitionException
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        existing_doc = self.make_document(id=doc_id, status=DocumentStatus.DRAFT.value)
        self.mock_doc_repo.get_by_id.return_value = existing_doc

        request = UpdateStatusRequest(new_status=DocumentStatus.APPROVED)
        service = self.get_instance()

        with self.assertRaises(InvalidStateTransitionException):
            service.execute(doc_id, request, self.fake.email())

    def test_execute_error_from_approved(self) -> None:
        """
        When: Trying to change from APPROVED (final state)
        Then: Should raise InvalidStateTransitionException
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        existing_doc = self.make_document(id=doc_id, status=DocumentStatus.APPROVED.value)
        self.mock_doc_repo.get_by_id.return_value = existing_doc

        request = UpdateStatusRequest(new_status=DocumentStatus.REJECTED)
        service = self.get_instance()

        with self.assertRaises(InvalidStateTransitionException):
            service.execute(doc_id, request, self.fake.email())
