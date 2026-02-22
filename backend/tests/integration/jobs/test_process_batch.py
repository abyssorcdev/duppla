"""Integration tests for ProcessBatch service (POST)."""

import pytest

from app.application.dtos.job_dtos import ProcessBatchRequest
from app.application.services.process_batch import ProcessBatch
from app.domain.exceptions import DocumentNotFoundException
from app.infrastructure.database.models import JobModel

from .conftest import create_documents, fake


class TestProcessBatch:
    """Verify ProcessBatch creates jobs in the database."""

    def test_create_job_with_valid_documents(self, db, mock_celery):
        """
        When: All document IDs exist
        Then: Job should persist in DB with status 'pending'
        """
        doc_ids = create_documents(db, count=2)

        result = ProcessBatch(db=db).execute(ProcessBatchRequest(document_ids=doc_ids))

        assert result.status == "pending"
        assert result.job_id is not None

        db.expire_all()
        row = db.query(JobModel).filter_by(id=result.job_id).first()
        assert row is not None
        assert row.status == "pending"
        assert set(row.document_ids) == set(doc_ids)

    def test_celery_task_dispatched(self, db, mock_celery):
        """
        When: Job is created successfully
        Then: Celery task should be dispatched with correct arguments
        """
        doc_ids = create_documents(db, count=2)

        result = ProcessBatch(db=db).execute(ProcessBatchRequest(document_ids=doc_ids))

        mock_celery.delay.assert_called_once_with(str(result.job_id), doc_ids)

    def test_document_not_found_raises(self, db, mock_celery):
        """
        When: One of the document IDs doesn't exist
        Then: Should raise DocumentNotFoundException
        """
        doc_ids = create_documents(db, count=1)
        not_found_id = fake.random_int(min=900_000, max=999_999)
        doc_ids.append(not_found_id)

        with pytest.raises(DocumentNotFoundException):
            ProcessBatch(db=db).execute(ProcessBatchRequest(document_ids=doc_ids))

        mock_celery.delay.assert_not_called()

    def test_validates_all_documents_before_creating_job(self, db, mock_celery):
        """
        When: First document exists but second doesn't
        Then: No job should be created in the database
        """
        doc_ids = create_documents(db, count=1)
        not_found_id = fake.random_int(min=900_000, max=999_999)
        doc_ids.append(not_found_id)

        initial_count = db.query(JobModel).count()

        with pytest.raises(DocumentNotFoundException):
            ProcessBatch(db=db).execute(ProcessBatchRequest(document_ids=doc_ids))

        assert db.query(JobModel).count() == initial_count
