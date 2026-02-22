"""Tests for app.application.services.process_batch.ProcessBatch."""

import unittest
from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase

from app.application.dtos.job_dtos import ProcessBatchRequest
from app.application.services.process_batch import ProcessBatch
from app.domain.entities.job.job import Job
from app.domain.entities.job.status import JobStatus
from app.domain.exceptions import DocumentNotFoundException


class ProcessBatchTestCase(BaseTestCase):
    """Global base class for ALL ProcessBatch tests."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.patcher_doc_repo = patch(
            "app.application.services.process_batch.DocumentRepository"
        )
        cls.patcher_job_repo = patch(
            "app.application.services.process_batch.JobRepository"
        )
        cls.patcher_celery_task = patch(
            "app.application.services.process_batch.process_documents_batch"
        )
        cls.MockDocumentRepository = cls.patcher_doc_repo.start()
        cls.MockJobRepository = cls.patcher_job_repo.start()
        cls.mock_celery_task = cls.patcher_celery_task.start()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.patcher_doc_repo.stop()
        cls.patcher_job_repo.stop()
        cls.patcher_celery_task.stop()

    def setUp(self) -> None:
        super().setUp()
        self.mock_db = self.make_mock_db_session()
        self.mock_doc_repo = MagicMock()
        self.mock_job_repo = MagicMock()
        self.MockDocumentRepository.return_value = self.mock_doc_repo
        self.MockJobRepository.return_value = self.mock_job_repo

    def tearDown(self) -> None:
        super().tearDown()
        self.MockDocumentRepository.reset_mock()
        self.MockJobRepository.reset_mock()
        self.mock_celery_task.reset_mock()

    def get_instance(self) -> ProcessBatch:
        return ProcessBatch(db=self.mock_db)


class TestUnderScoreUnderScoreInit(ProcessBatchTestCase):
    """Tests for __init__()."""

    def test_init_success_creates_repositories(self) -> None:
        """
        When: ProcessBatch is initialized
        Then: Should create both repositories
        """
        service = self.get_instance()
        self.MockDocumentRepository.assert_called_once_with(self.mock_db)
        self.MockJobRepository.assert_called_once_with(self.mock_db)

    def test_init_success_sets_attributes(self) -> None:
        """
        When: ProcessBatch is initialized
        Then: Should have document_repository and job_repository
        """
        service = self.get_instance()
        self.assertIsNotNone(service.document_repository)
        self.assertIsNotNone(service.job_repository)

    def test_init_success_accepts_session(self) -> None:
        """
        When: Initialized with any session
        Then: Should not raise
        """
        service = ProcessBatch(db=MagicMock())
        self.assertIsNotNone(service)


class TestExecute(ProcessBatchTestCase):
    """Tests for execute()."""

    def test_execute_success_creates_job(self) -> None:
        """
        When: All document IDs exist
        Then: Should create job and return response
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        self.mock_doc_repo.get_by_id.return_value = self.make_document(id=doc_id)
        created_job = self.make_job(document_ids=[doc_id])
        self.mock_job_repo.create.return_value = created_job

        request = ProcessBatchRequest(document_ids=[doc_id])
        service = self.get_instance()
        result = service.execute(request)

        self.assertEqual(result.status, JobStatus.PENDING.value)
        self.mock_job_repo.create.assert_called_once()

    def test_execute_success_dispatches_celery_task(self) -> None:
        """
        When: Job is created successfully
        Then: Should dispatch Celery task
        """
        doc_ids = [self.fake.random_int(min=1, max=999) for _ in range(2)]
        self.mock_doc_repo.get_by_id.return_value = self.make_document(id=doc_ids[0])
        created_job = self.make_job(document_ids=doc_ids)
        self.mock_job_repo.create.return_value = created_job

        request = ProcessBatchRequest(document_ids=doc_ids)
        service = self.get_instance()
        service.execute(request)

        self.mock_celery_task.delay.assert_called_once()

    def test_execute_success_multiple_documents(self) -> None:
        """
        When: Multiple valid document IDs
        Then: Should validate all and create job
        """
        doc_ids = [self.fake.random_int(min=1, max=999) for _ in range(3)]
        self.mock_doc_repo.get_by_id.return_value = self.make_document()
        created_job = self.make_job(document_ids=doc_ids)
        self.mock_job_repo.create.return_value = created_job

        request = ProcessBatchRequest(document_ids=doc_ids)
        service = self.get_instance()
        result = service.execute(request)

        self.assertEqual(self.mock_doc_repo.get_by_id.call_count, 3)

    def test_execute_success_returns_job_response(self) -> None:
        """
        When: Job is created
        Then: Should return response with all fields
        """
        self.mock_doc_repo.get_by_id.return_value = self.make_document()
        created_job = self.make_job()
        self.mock_job_repo.create.return_value = created_job

        request = ProcessBatchRequest(document_ids=[1])
        service = self.get_instance()
        result = service.execute(request)

        self.assertIsNotNone(result.job_id)
        self.assertIsNotNone(result.status)
        self.assertIsNotNone(result.created_at)

    def test_execute_error_document_not_found(self) -> None:
        """
        When: One of the document IDs doesn't exist
        Then: Should raise DocumentNotFoundException
        """
        self.mock_doc_repo.get_by_id.side_effect = [
            self.make_document(id=1),
            None,
        ]

        request = ProcessBatchRequest(document_ids=[1, 999])
        service = self.get_instance()

        with self.assertRaises(DocumentNotFoundException):
            service.execute(request)

    def test_execute_error_first_document_missing(self) -> None:
        """
        When: First document ID doesn't exist
        Then: Should raise DocumentNotFoundException immediately
        """
        self.mock_doc_repo.get_by_id.return_value = None

        request = ProcessBatchRequest(document_ids=[999])
        service = self.get_instance()

        with self.assertRaises(DocumentNotFoundException):
            service.execute(request)

        self.mock_job_repo.create.assert_not_called()

    def test_execute_error_no_celery_on_failure(self) -> None:
        """
        When: Document validation fails
        Then: Should not dispatch Celery task
        """
        self.mock_doc_repo.get_by_id.return_value = None

        request = ProcessBatchRequest(document_ids=[999])
        service = self.get_instance()

        with self.assertRaises(DocumentNotFoundException):
            service.execute(request)

        self.mock_celery_task.delay.assert_not_called()
