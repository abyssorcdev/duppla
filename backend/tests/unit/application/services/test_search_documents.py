"""Tests for app.application.services.search_documents.SearchDocuments."""

import unittest
from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase

from app.application.dtos.document_dtos import SearchDocumentsRequest
from app.application.services.search_documents import SearchDocuments
from app.domain.entities.document.document import Document
from app.domain.entities.document.status import DocumentStatus


class SearchDocumentsTestCase(BaseTestCase):
    """Global base class for ALL SearchDocuments tests."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.patcher_repo = patch(
            "app.application.services.search_documents.DocumentRepository"
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

    def get_instance(self) -> SearchDocuments:
        return SearchDocuments(db=self.mock_db)


class TestUnderScoreUnderScoreInit(SearchDocumentsTestCase):
    """Tests for __init__()."""

    def test_init_success_creates_repository(self) -> None:
        """
        When: SearchDocuments is initialized
        Then: Should create DocumentRepository
        """
        service = self.get_instance()
        self.MockDocumentRepository.assert_called_once_with(self.mock_db)

    def test_init_success_sets_repository(self) -> None:
        """
        When: SearchDocuments is initialized
        Then: Should have repository attribute
        """
        service = self.get_instance()
        self.assertIsNotNone(service.repository)

    def test_init_success_accepts_session(self) -> None:
        """
        When: Initialized with any session
        Then: Should not raise
        """
        service = SearchDocuments(db=MagicMock())
        self.assertIsNotNone(service)


class TestExecute(SearchDocumentsTestCase):
    """Tests for execute()."""

    def test_execute_success_returns_paginated_response(self) -> None:
        """
        When: Search returns documents
        Then: Should return PaginatedDocumentsResponse
        """
        docs = [self.make_document(id=i) for i in range(1, 4)]
        self.mock_repo_instance.search.return_value = (docs, 3)

        request = SearchDocumentsRequest()
        service = self.get_instance()
        result = service.execute(request)

        self.assertEqual(len(result.items), 3)
        self.assertEqual(result.total, 3)
        self.assertEqual(result.page, 1)

    def test_execute_success_empty_results(self) -> None:
        """
        When: Search returns no documents
        Then: Should return empty items with total=0
        """
        self.mock_repo_instance.search.return_value = ([], 0)

        request = SearchDocumentsRequest()
        service = self.get_instance()
        result = service.execute(request)

        self.assertEqual(len(result.items), 0)
        self.assertEqual(result.total, 0)
        self.assertEqual(result.total_pages, 0)

    def test_execute_success_with_type_filter(self) -> None:
        """
        When: Filtering by type
        Then: Should pass type filter to repository
        """
        self.mock_repo_instance.search.return_value = ([], 0)

        request = SearchDocumentsRequest(type="invoice")
        service = self.get_instance()
        service.execute(request)

        call_kwargs = self.mock_repo_instance.search.call_args
        filters = call_kwargs.kwargs.get("filters") or call_kwargs[1].get("filters", call_kwargs[0][0])
        self.assertIn("type", filters)
        self.assertEqual(filters["type"], "invoice")

    def test_execute_success_with_status_filter(self) -> None:
        """
        When: Filtering by status
        Then: Should pass status filter to repository
        """
        self.mock_repo_instance.search.return_value = ([], 0)

        request = SearchDocumentsRequest(status="pending")
        service = self.get_instance()
        service.execute(request)

        call_kwargs = self.mock_repo_instance.search.call_args
        filters = call_kwargs.kwargs.get("filters") or call_kwargs[1].get("filters", call_kwargs[0][0])
        self.assertIn("status", filters)

    def test_execute_success_pagination_calculation(self) -> None:
        """
        When: Total exceeds page_size
        Then: Should calculate total_pages correctly
        """
        docs = [self.make_document(id=1)]
        self.mock_repo_instance.search.return_value = (docs, 25)

        request = SearchDocumentsRequest(page=1, page_size=10)
        service = self.get_instance()
        result = service.execute(request)

        self.assertEqual(result.total_pages, 3)
        self.assertEqual(result.page_size, 10)

    def test_execute_success_skip_calculation(self) -> None:
        """
        When: Requesting page 3 with page_size 10
        Then: Should pass skip=20 to repository
        """
        self.mock_repo_instance.search.return_value = ([], 0)

        request = SearchDocumentsRequest(page=3, page_size=10)
        service = self.get_instance()
        service.execute(request)

        call_kwargs = self.mock_repo_instance.search.call_args
        skip = call_kwargs.kwargs.get("skip") or call_kwargs[1].get("skip", call_kwargs[0][1] if len(call_kwargs[0]) > 1 else None)
        self.assertEqual(skip, 20)

    def test_execute_success_no_filters(self) -> None:
        """
        When: No filters are provided
        Then: Should pass filters dict with all None values
        """
        self.mock_repo_instance.search.return_value = ([], 0)

        request = SearchDocumentsRequest()
        service = self.get_instance()
        service.execute(request)

        self.mock_repo_instance.search.assert_called_once()
        call_args = self.mock_repo_instance.search.call_args
        if call_args.kwargs.get("filters") is not None:
            filters = call_args.kwargs["filters"]
        else:
            filters = call_args[1].get("filters", call_args[0][0] if call_args[0] else {})
        non_none_values = [k for k, v in filters.items() if v is not None]
        self.assertEqual(len(non_none_values), 0)

    def test_execute_error_repository_raises(self) -> None:
        """
        When: Repository raises exception
        Then: Should propagate
        """
        self.mock_repo_instance.search.side_effect = Exception("DB error")

        request = SearchDocumentsRequest()
        service = self.get_instance()

        with self.assertRaises(Exception):
            service.execute(request)
