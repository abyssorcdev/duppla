"""Process batch service.

Handles batch processing job creation and delegation to Celery.
"""

from sqlalchemy.orm import Session

from app.application.dtos.job_dtos import JobResponse, ProcessBatchRequest
from app.domain.entities.job import Job
from app.domain.exceptions import DocumentNotFoundException
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.job_repository import JobRepository


class ProcessBatch:
    """Service for creating and processing batch jobs."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session.

        Args:
            db: Database session
        """
        self.document_repository = DocumentRepository(db)
        self.job_repository = JobRepository(db)

    def execute(self, request: ProcessBatchRequest) -> JobResponse:
        """Execute batch processing job creation.

        Args:
            request: Batch processing request with document IDs

        Returns:
            Job response with pending status

        Raises:
            DocumentNotFoundException: If any document ID doesn't exist
        """
        for document_id in request.document_ids:
            document = self.document_repository.get_by_id(document_id)
            if not document:
                raise DocumentNotFoundException(document_id)

        job = Job(document_ids=request.document_ids)

        created_job = self.job_repository.create(job)

        # TODO: Publish Celery task (will be implemented in Fase 6)
        # from app.infrastructure.notifications.tasks.celery_tasks import process_batch
        # process_batch.delay(str(created_job.id), created_job.document_ids)

        return JobResponse(
            job_id=created_job.id,
            status=created_job.status,
            created_at=created_job.created_at,
            completed_at=created_job.completed_at,
            result=created_job.result,
            error_message=created_job.error_message,
        )
