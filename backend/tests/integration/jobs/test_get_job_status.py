"""Integration tests for GetJobStatus service (GET)."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.application.dtos.job_dtos import ProcessBatchRequest
from app.application.services.get_job_status import GetJobStatus
from app.application.services.process_batch import ProcessBatch
from app.domain.exceptions import JobNotFoundException
from app.infrastructure.repositories.job_repository import JobRepository

from .conftest import create_documents, fake


class TestGetJobStatus:
    """Verify GetJobStatus reads job data from the database."""

    def test_get_pending_job(self, db, mock_celery):
        """
        When: A job was just created
        Then: GetJobStatus should return it with status 'pending'
        """
        doc_ids = create_documents(db, count=1)
        created = ProcessBatch(db=db).execute(ProcessBatchRequest(document_ids=doc_ids))

        result = GetJobStatus(db=db).execute(created.job_id)

        assert result.job_id == created.job_id
        assert result.status == "pending"
        assert result.created_at is not None
        assert result.completed_at is None

    def test_get_completed_job(self, db, mock_celery):
        """
        When: A job has been completed
        Then: GetJobStatus should return result and completed_at
        """
        doc_ids = create_documents(db, count=1)
        created = ProcessBatch(db=db).execute(ProcessBatchRequest(document_ids=doc_ids))

        processed = fake.random_int(min=1, max=10)
        job_result = {"total": processed, "processed": processed, "failed": 0}

        job_repo = JobRepository(db)
        job_repo.update_status(
            created.job_id,
            "completed",
            completed_at=datetime.now(timezone.utc),
            result=job_result,
        )

        result = GetJobStatus(db=db).execute(created.job_id)

        assert result.status == "completed"
        assert result.completed_at is not None
        assert result.result == job_result

    def test_get_failed_job(self, db, mock_celery):
        """
        When: A job has failed
        Then: GetJobStatus should return error_message
        """
        doc_ids = create_documents(db, count=1)
        created = ProcessBatch(db=db).execute(ProcessBatchRequest(document_ids=doc_ids))

        error_msg = fake.sentence()

        job_repo = JobRepository(db)
        job_repo.update_status(
            created.job_id,
            "failed",
            completed_at=datetime.now(timezone.utc),
            error_message=error_msg,
        )

        result = GetJobStatus(db=db).execute(created.job_id)

        assert result.status == "failed"
        assert result.error_message == error_msg

    def test_get_nonexistent_job(self, db):
        """
        When: Job UUID does not exist
        Then: Should raise JobNotFoundException
        """
        with pytest.raises(JobNotFoundException):
            GetJobStatus(db=db).execute(uuid4())
