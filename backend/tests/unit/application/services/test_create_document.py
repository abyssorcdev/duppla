"""Tests for app.application.services.create_document.CreateDocument."""

import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase

from app.application.dtos.document_dtos import CreateDocumentRequest
from app.application.services.create_document import CreateDocument
from app.domain.entities.document.document import Document
from app.domain.entities.document.status import DocumentStatus
from app.domain.exceptions import InvalidAmountException


class CreateDocumentTestCase(BaseTestCase):
    """Global base class for ALL CreateDocument tests."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.patcher_repo = patch(
            "app.application.services.create_document.DocumentRepository"
        )
        cls.patcher_audit = patch(
            "app.application.services.create_document.AuditRepository"
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

    def get_instance(self) -> CreateDocument:
        return CreateDocument(db=self.mock_db)


class TestUnderScoreUnderScoreInit(CreateDocumentTestCase):
    """Tests for __init__()."""

    def test_init_success_creates_repositories(self) -> None:
        """
        When: CreateDocument is initialized with db session
        Then: Should create repository instances
        """
        service = self.get_instance()
        self.MockDocumentRepository.assert_called_once_with(self.mock_db)
        self.MockAuditRepository.assert_called_once_with(self.mock_db)

    def test_init_success_sets_attributes(self) -> None:
        """
        When: CreateDocument is initialized
        Then: Should set repository and audit_repository attributes
        """
        service = self.get_instance()
        self.assertIsNotNone(service.repository)
        self.assertIsNotNone(service.audit_repository)

    def test_init_success_accepts_mock_db(self) -> None:
        """
        When: CreateDocument is initialized with a MagicMock session
        Then: Should not raise any errors
        """
        service = CreateDocument(db=MagicMock())
        self.assertIsNotNone(service)


class TestExecute(CreateDocumentTestCase):
    """Tests for execute()."""

    def test_execute_success_creates_document(self) -> None:
        """
        When: Valid CreateDocumentRequest is provided
        Then: Should create document and return DocumentResponse
        """
        doc_type = "invoice"
        amount = Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True)))
        metadata = {"client": self.fake.company()}
        created_by = self.fake.bothify("user-####")
        doc_id = self.fake.random_int(min=1, max=99_999)

        request = CreateDocumentRequest(
            type=doc_type,
            amount=amount,
            metadata=metadata,
            created_by=created_by,
        )
        created_doc = self.make_document(
            id=doc_id, type=doc_type, amount=amount,
            metadata=metadata, created_by=created_by,
        )
        self.mock_repo_instance.create.return_value = created_doc

        service = self.get_instance()
        result = service.execute(request)

        self.assertEqual(result.id, doc_id)
        self.assertEqual(result.type, doc_type)
        self.assertEqual(result.amount, amount)
        self.assertEqual(result.status, DocumentStatus.DRAFT.value)
        self.mock_repo_instance.create.assert_called_once()

    def test_execute_success_logs_audit(self) -> None:
        """
        When: Document is created successfully
        Then: Should log audit entry
        """
        doc_type = "receipt"
        amount = Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True)))
        created_by = self.fake.bothify("user-####")
        doc_id = self.fake.random_int(min=1, max=99_999)

        request = CreateDocumentRequest(
            type=doc_type,
            amount=amount,
            created_by=created_by,
        )
        created_doc = self.make_document(
            id=doc_id, type=doc_type, amount=amount, created_by=created_by,
        )
        self.mock_repo_instance.create.return_value = created_doc

        service = self.get_instance()
        service.execute(request)

        self.mock_audit_instance.log_created.assert_called_once()
        call_kwargs = self.mock_audit_instance.log_created.call_args
        self.assertEqual(call_kwargs.kwargs.get("table_name") or call_kwargs[1].get("table_name", call_kwargs[0][0]), "documents")

    def test_execute_success_with_empty_metadata(self) -> None:
        """
        When: Request has no metadata
        Then: Should create document with empty metadata
        """
        doc_type = "voucher"
        amount = Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True)))
        created_by = self.fake.bothify("user-####")
        doc_id = self.fake.random_int(min=1, max=99_999)

        request = CreateDocumentRequest(
            type=doc_type,
            amount=amount,
            created_by=created_by,
        )
        created_doc = self.make_document(
            id=doc_id, type=doc_type, amount=amount,
            metadata={}, created_by=created_by,
        )
        self.mock_repo_instance.create.return_value = created_doc

        service = self.get_instance()
        result = service.execute(request)

        self.assertEqual(result.id, doc_id)

    def test_execute_success_returns_document_response(self) -> None:
        """
        When: Document is created
        Then: Response should have all required fields
        """
        amount = Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True)))
        doc_id = self.fake.random_int(min=1, max=99_999)

        request = CreateDocumentRequest(
            type="invoice",
            amount=amount,
        )
        created_doc = self.make_document(id=doc_id, amount=amount)
        self.mock_repo_instance.create.return_value = created_doc

        service = self.get_instance()
        result = service.execute(request)

        self.assertIsNotNone(result.id)
        self.assertIsNotNone(result.type)
        self.assertIsNotNone(result.amount)
        self.assertIsNotNone(result.status)
        self.assertIsNotNone(result.created_at)
        self.assertIsNotNone(result.updated_at)

    def test_execute_success_passes_created_by(self) -> None:
        """
        When: Request includes created_by
        Then: Document should be created with that user
        """
        created_by = self.fake.email()
        doc_id = self.fake.random_int(min=1, max=99_999)

        request = CreateDocumentRequest(
            type="invoice",
            amount=Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True))),
            created_by=created_by,
        )
        created_doc = self.make_document(
            id=doc_id, created_by=created_by,
        )
        self.mock_repo_instance.create.return_value = created_doc

        service = self.get_instance()
        result = service.execute(request)

        self.assertEqual(result.created_by, created_by)

    def test_execute_error_repository_raises(self) -> None:
        """
        When: Repository raises an exception
        Then: Should propagate the exception
        """
        error_msg = self.fake.sentence()
        request = CreateDocumentRequest(
            type="invoice",
            amount=Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True))),
        )
        self.mock_repo_instance.create.side_effect = Exception(error_msg)

        service = self.get_instance()

        with self.assertRaises(Exception) as ctx:
            service.execute(request)

        self.assertIn(error_msg, str(ctx.exception))
