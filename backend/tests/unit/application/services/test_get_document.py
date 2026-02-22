"""Tests for app.application.services.get_document.GetDocument."""

import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase

from app.application.services.get_document import GetDocument
from app.domain.entities.document.document import Document
from app.domain.entities.document.status import DocumentStatus
from app.domain.exceptions import DocumentNotFoundException


class GetDocumentTestCase(BaseTestCase):
    """Global base class for ALL GetDocument tests."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.patcher_repo = patch(
            "app.application.services.get_document.DocumentRepository"
        )
        cls.MockDocumentRepository = cls.patcher_repo.start()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.patcher_repo.stop()

    def setUp(self) -> None:
        super().setUp()
        self.mock_db = self.make_mock_db_session()
        self.mock_repo_instance = MagicMock()
        self.MockDocumentRepository.return_value = self.mock_repo_instance

    def tearDown(self) -> None:
        super().tearDown()
        self.MockDocumentRepository.reset_mock()

    def get_instance(self) -> GetDocument:
        return GetDocument(db=self.mock_db)


class TestUnderScoreUnderScoreInit(GetDocumentTestCase):
    """Tests for __init__()."""

    def test_init_success_creates_repository(self) -> None:
        """
        When: GetDocument is initialized
        Then: Should create DocumentRepository
        """
        service = self.get_instance()
        self.MockDocumentRepository.assert_called_once_with(self.mock_db)

    def test_init_success_sets_repository(self) -> None:
        """
        When: GetDocument is initialized
        Then: Should set repository attribute
        """
        service = self.get_instance()
        self.assertIsNotNone(service.repository)

    def test_init_success_accepts_db_session(self) -> None:
        """
        When: Initialized with any session
        Then: Should not raise errors
        """
        service = GetDocument(db=MagicMock())
        self.assertIsNotNone(service)


class TestExecute(GetDocumentTestCase):
    """Tests for execute()."""

    def test_execute_success_returns_document(self) -> None:
        """
        When: Document with given ID exists
        Then: Should return DocumentResponse with correct data
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        doc = self.make_document(id=doc_id)
        self.mock_repo_instance.get_by_id.return_value = doc

        service = self.get_instance()
        result = service.execute(doc_id)

        self.assertEqual(result.id, doc_id)
        self.assertEqual(result.type, doc.type)
        self.assertEqual(result.amount, doc.amount)

    def test_execute_success_response_fields(self) -> None:
        """
        When: Document is found
        Then: Response should contain all fields
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        created_by = self.fake.bothify("user-####")
        doc = self.make_document(id=doc_id, type="receipt", created_by=created_by)
        self.mock_repo_instance.get_by_id.return_value = doc

        service = self.get_instance()
        result = service.execute(doc_id)

        self.assertIsNotNone(result.id)
        self.assertIsNotNone(result.type)
        self.assertIsNotNone(result.amount)
        self.assertIsNotNone(result.status)
        self.assertIsNotNone(result.created_at)
        self.assertIsNotNone(result.updated_at)
        self.assertIsNotNone(result.metadata)

    def test_execute_success_calls_repository(self) -> None:
        """
        When: execute() is called
        Then: Should call repository.get_by_id with correct ID
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        doc = self.make_document(id=doc_id)
        self.mock_repo_instance.get_by_id.return_value = doc

        service = self.get_instance()
        service.execute(doc_id)

        self.mock_repo_instance.get_by_id.assert_called_once_with(doc_id)

    def test_execute_error_document_not_found(self) -> None:
        """
        When: Document does not exist
        Then: Should raise DocumentNotFoundException
        """
        not_found_id = self.fake.random_int(min=100_000, max=999_999)
        self.mock_repo_instance.get_by_id.return_value = None

        service = self.get_instance()

        with self.assertRaises(DocumentNotFoundException) as ctx:
            service.execute(not_found_id)

        self.assertEqual(ctx.exception.document_id, not_found_id)

    def test_execute_error_repository_raises(self) -> None:
        """
        When: Repository raises unexpected exception
        Then: Should propagate the exception
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        self.mock_repo_instance.get_by_id.side_effect = Exception(self.fake.sentence())

        service = self.get_instance()

        with self.assertRaises(Exception):
            service.execute(doc_id)

    def test_execute_success_preserves_metadata(self) -> None:
        """
        When: Document has metadata
        Then: Response should include the metadata
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        metadata = {"client": self.fake.company(), "email": self.fake.company_email()}
        doc = self.make_document(id=doc_id, metadata=metadata)
        self.mock_repo_instance.get_by_id.return_value = doc

        service = self.get_instance()
        result = service.execute(doc_id)

        self.assertEqual(result.metadata, metadata)
