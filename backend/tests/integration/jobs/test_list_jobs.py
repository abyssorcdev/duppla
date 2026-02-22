"""Integration tests for ListJobs service (GET)."""

from datetime import datetime, timezone

from app.application.dtos.job_dtos import ProcessBatchRequest
from app.application.services.list_jobs import ListJobs
from app.application.services.process_batch import ProcessBatch
from app.infrastructure.repositories.job_repository import JobRepository

from .conftest import create_documents, fake


class TestListJobs:
    """Verify ListJobs queries real data from the database."""

    def test_list_returns_created_jobs(self, db, mock_celery):
        """
        When: Multiple jobs exist
        Then: ListJobs should return them in a paginated response
        """
        for _ in range(3):
            doc_ids = create_documents(db, count=1)
            ProcessBatch(db=db).execute(ProcessBatchRequest(document_ids=doc_ids))

        result = ListJobs(db=db).execute()

        assert result.total >= 3
        assert len(result.items) >= 3

    def test_list_empty(self, db):
        """
        When: No jobs exist
        Then: Should return empty items with total=0
        """
        result = ListJobs(db=db).execute()

        assert result.total == 0
        assert len(result.items) == 0
        assert result.total_pages == 1

    def test_list_filter_by_status(self, db, mock_celery):
        """
        When: Jobs exist with different statuses
        Then: Filtering by status should return only matching jobs
        """
        doc_ids = create_documents(db, count=1)
        created = ProcessBatch(db=db).execute(ProcessBatchRequest(document_ids=doc_ids))

        processed = fake.random_int(min=1, max=10)
        job_repo = JobRepository(db)
        job_repo.update_status(
            created.job_id,
            "completed",
            completed_at=datetime.now(timezone.utc),
            result={"total": processed, "processed": processed, "failed": 0},
        )

        doc_ids2 = create_documents(db, count=1)
        ProcessBatch(db=db).execute(ProcessBatchRequest(document_ids=doc_ids2))

        completed = ListJobs(db=db).execute(status="completed")
        pending = ListJobs(db=db).execute(status="pending")

        assert all(item.status == "completed" for item in completed.items)
        assert all(item.status == "pending" for item in pending.items)

    def test_list_pagination(self, db, mock_celery):
        """
        When: More jobs exist than page_size
        Then: Should return paginated results
        """
        for _ in range(5):
            doc_ids = create_documents(db, count=1)
            ProcessBatch(db=db).execute(ProcessBatchRequest(document_ids=doc_ids))

        page1 = ListJobs(db=db).execute(page=1, page_size=2)

        assert len(page1.items) == 2
        assert page1.total >= 5
        assert page1.page == 1
        assert page1.page_size == 2
        assert page1.total_pages >= 3
