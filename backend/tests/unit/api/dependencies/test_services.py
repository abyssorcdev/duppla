"""Tests for app.api.dependencies.services – service factory functions."""

from unittest.mock import MagicMock

from tests.common import BaseTestCase

from app.api.dependencies.services import (
    get_create_document_service,
    get_get_document_service,
    get_get_job_status_service,
    get_list_jobs_service,
    get_process_batch_service,
    get_search_documents_service,
    get_update_document_service,
    get_update_status_service,
)
from app.application.services import (
    CreateDocument,
    GetDocument,
    GetJobStatus,
    ListJobs,
    ProcessBatch,
    SearchDocuments,
    UpdateDocument,
    UpdateStatus,
)


class TestServiceFactories(BaseTestCase):
    """Tests for all service dependency factories."""

    def setUp(self) -> None:
        super().setUp()
        self.mock_db = self.make_mock_db_session()

    def test_get_create_document_service_success(self) -> None:
        svc = get_create_document_service(db=self.mock_db)
        self.assertIsInstance(svc, CreateDocument)

    def test_get_get_document_service_success(self) -> None:
        svc = get_get_document_service(db=self.mock_db)
        self.assertIsInstance(svc, GetDocument)

    def test_get_update_document_service_success(self) -> None:
        svc = get_update_document_service(db=self.mock_db)
        self.assertIsInstance(svc, UpdateDocument)

    def test_get_update_status_service_success(self) -> None:
        svc = get_update_status_service(db=self.mock_db)
        self.assertIsInstance(svc, UpdateStatus)

    def test_get_search_documents_service_success(self) -> None:
        svc = get_search_documents_service(db=self.mock_db)
        self.assertIsInstance(svc, SearchDocuments)

    def test_get_process_batch_service_success(self) -> None:
        svc = get_process_batch_service(db=self.mock_db)
        self.assertIsInstance(svc, ProcessBatch)

    def test_get_get_job_status_service_success(self) -> None:
        svc = get_get_job_status_service(db=self.mock_db)
        self.assertIsInstance(svc, GetJobStatus)

    def test_get_list_jobs_service_success(self) -> None:
        svc = get_list_jobs_service(db=self.mock_db)
        self.assertIsInstance(svc, ListJobs)
