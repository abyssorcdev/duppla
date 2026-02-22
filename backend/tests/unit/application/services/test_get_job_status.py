"""Tests for app.application.services.get_job_status.GetJobStatus."""

import unittest
from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase

from app.application.services.get_job_status import GetJobStatus
from app.domain.entities.job.job import Job
from app.domain.entities.job.status import JobStatus
from app.domain.exceptions import JobNotFoundException


class GetJobStatusTestCase(BaseTestCase):
    """Global base class for ALL GetJobStatus tests."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.patcher_repo = patch(
            "app.application.services.get_job_status.JobRepository"
        )
        cls.MockJobRepository = cls.patcher_repo.start()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls.patcher_repo.stop()

    def setUp(self) -> None:
        super().setUp()
        self.mock_db = self.make_mock_db_session()
        self.mock_repo_instance = MagicMock()
        self.MockJobRepository.return_value = self.mock_repo_instance

    def tearDown(self) -> None:
        super().tearDown()
        self.MockJobRepository.reset_mock()

    def get_instance(self) -> GetJobStatus:
        return GetJobStatus(db=self.mock_db)


class TestUnderScoreUnderScoreInit(GetJobStatusTestCase):
    """Tests for __init__()."""

    def test_init_success_creates_repository(self) -> None:
        """
        When: GetJobStatus is initialized
        Then: Should create JobRepository
        """
        service = self.get_instance()
        self.MockJobRepository.assert_called_once_with(self.mock_db)

    def test_init_success_sets_repository(self) -> None:
        """
        When: GetJobStatus is initialized
        Then: Should have repository attribute
        """
        service = self.get_instance()
        self.assertIsNotNone(service.repository)

    def test_init_success_accepts_session(self) -> None:
        """
        When: Initialized with any session
        Then: Should not raise
        """
        service = GetJobStatus(db=MagicMock())
        self.assertIsNotNone(service)


class TestExecute(GetJobStatusTestCase):
    """Tests for execute()."""

    def test_execute_success_returns_job_response(self) -> None:
        """
        When: Job with given UUID exists
        Then: Should return JobResponse
        """
        job = self.make_job()
        self.mock_repo_instance.get_by_id.return_value = job

        service = self.get_instance()
        result = service.execute(self.test_uuid)

        self.assertEqual(result.job_id, self.test_uuid)
        self.assertEqual(result.status, JobStatus.PENDING.value)

    def test_execute_success_completed_job(self) -> None:
        """
        When: Job is completed
        Then: Should return result and completed_at
        """
        job = self.make_job()
        job.complete({"total": 3, "processed": 3, "failed": 0})
        self.mock_repo_instance.get_by_id.return_value = job

        service = self.get_instance()
        result = service.execute(self.test_uuid)

        self.assertEqual(result.status, JobStatus.COMPLETED.value)
        self.assertIsNotNone(result.completed_at)
        self.assertIsNotNone(result.result)

    def test_execute_success_failed_job(self) -> None:
        """
        When: Job has failed
        Then: Should return error_message
        """
        error_msg = self.fake.sentence()
        job = self.make_job()
        job.fail(error_msg)
        self.mock_repo_instance.get_by_id.return_value = job

        service = self.get_instance()
        result = service.execute(self.test_uuid)

        self.assertEqual(result.status, JobStatus.FAILED.value)
        self.assertEqual(result.error_message, error_msg)

    def test_execute_success_calls_repository(self) -> None:
        """
        When: execute() is called
        Then: Should call repository.get_by_id with the UUID
        """
        job = self.make_job()
        self.mock_repo_instance.get_by_id.return_value = job

        service = self.get_instance()
        service.execute(self.test_uuid)

        self.mock_repo_instance.get_by_id.assert_called_once_with(self.test_uuid)

    def test_execute_error_job_not_found(self) -> None:
        """
        When: Job does not exist
        Then: Should raise JobNotFoundException
        """
        self.mock_repo_instance.get_by_id.return_value = None

        service = self.get_instance()

        with self.assertRaises(JobNotFoundException):
            service.execute(self.test_uuid)

    def test_execute_error_repository_raises(self) -> None:
        """
        When: Repository raises unexpected exception
        Then: Should propagate
        """
        error_msg = self.fake.sentence()
        self.mock_repo_instance.get_by_id.side_effect = Exception(error_msg)

        service = self.get_instance()

        with self.assertRaises(Exception):
            service.execute(self.test_uuid)

    def test_execute_success_processing_job(self) -> None:
        """
        When: Job is currently processing
        Then: Should return PROCESSING status
        """
        job = self.make_job()
        job.start_processing()
        self.mock_repo_instance.get_by_id.return_value = job

        service = self.get_instance()
        result = service.execute(self.test_uuid)

        self.assertEqual(result.status, JobStatus.PROCESSING.value)
