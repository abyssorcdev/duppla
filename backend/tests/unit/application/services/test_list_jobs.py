"""Tests for app.application.services.list_jobs.ListJobs."""

import unittest
from unittest.mock import MagicMock, patch

from tests.common import BaseTestCase
from app.application.services.list_jobs import ListJobs
from app.domain.entities.job.job import Job
from app.domain.entities.job.status import JobStatus


class ListJobsTestCase(BaseTestCase):
    """Global base class for ALL ListJobs tests."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.patcher_repo = patch(
            "app.application.services.list_jobs.JobRepository"
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

    def get_instance(self) -> ListJobs:
        return ListJobs(db=self.mock_db)


class TestUnderScoreUnderScoreInit(ListJobsTestCase):
    """Tests for __init__()."""

    def test_init_success_creates_repository(self) -> None:
        """
        When: ListJobs is initialized
        Then: Should create JobRepository
        """
        service = self.get_instance()
        self.MockJobRepository.assert_called_once_with(self.mock_db)

    def test_init_success_sets_repository(self) -> None:
        """
        When: ListJobs is initialized
        Then: Should have repository attribute
        """
        service = self.get_instance()
        self.assertIsNotNone(service.repository)

    def test_init_success_accepts_session(self) -> None:
        """
        When: Initialized with any session
        Then: Should not raise
        """
        service = ListJobs(db=MagicMock())
        self.assertIsNotNone(service)


class TestExecute(ListJobsTestCase):
    """Tests for execute()."""

    def test_execute_success_returns_list(self) -> None:
        """
        When: Jobs exist
        Then: Should return paginated list
        """
        jobs = [self.make_job() for _ in range(3)]
        self.mock_repo_instance.list_all.return_value = (jobs, 3)

        service = self.get_instance()
        result = service.execute()

        self.assertEqual(len(result.items), 3)
        self.assertEqual(result.total, 3)

    def test_execute_success_empty_list(self) -> None:
        """
        When: No jobs exist
        Then: Should return empty list
        """
        self.mock_repo_instance.list_all.return_value = ([], 0)

        service = self.get_instance()
        result = service.execute()

        self.assertEqual(len(result.items), 0)
        self.assertEqual(result.total, 0)
        self.assertEqual(result.total_pages, 1)

    def test_execute_success_with_status_filter(self) -> None:
        """
        When: Filtering by status
        Then: Should pass status to repository
        """
        self.mock_repo_instance.list_all.return_value = ([], 0)

        service = self.get_instance()
        service.execute(status="completed")

        call_kwargs = self.mock_repo_instance.list_all.call_args
        self.assertEqual(
            call_kwargs.kwargs.get("status") or call_kwargs[1].get("status"),
            "completed",
        )

    def test_execute_success_pagination_params(self) -> None:
        """
        When: Page 2 with page_size 5
        Then: Should pass skip=5 and limit=5
        """
        self.mock_repo_instance.list_all.return_value = ([], 0)

        service = self.get_instance()
        service.execute(page=2, page_size=5)

        call_kwargs = self.mock_repo_instance.list_all.call_args
        skip = call_kwargs.kwargs.get("skip") or call_kwargs[1].get("skip")
        limit = call_kwargs.kwargs.get("limit") or call_kwargs[1].get("limit")
        self.assertEqual(skip, 5)
        self.assertEqual(limit, 5)

    def test_execute_success_total_pages_calculation(self) -> None:
        """
        When: Total is 25 and page_size is 10
        Then: total_pages should be 3
        """
        jobs = [self.make_job()]
        self.mock_repo_instance.list_all.return_value = (jobs, 25)

        service = self.get_instance()
        result = service.execute(page_size=10)

        self.assertEqual(result.total_pages, 3)

    def test_execute_success_default_pagination(self) -> None:
        """
        When: No pagination params provided
        Then: Should use defaults (page=1, page_size=10)
        """
        self.mock_repo_instance.list_all.return_value = ([], 0)

        service = self.get_instance()
        result = service.execute()

        self.assertEqual(result.page, 1)
        self.assertEqual(result.page_size, 10)

    def test_execute_error_repository_raises(self) -> None:
        """
        When: Repository raises exception
        Then: Should propagate
        """
        error_msg = self.fake.sentence()
        self.mock_repo_instance.list_all.side_effect = Exception(error_msg)

        service = self.get_instance()

        with self.assertRaises(Exception):
            service.execute()
