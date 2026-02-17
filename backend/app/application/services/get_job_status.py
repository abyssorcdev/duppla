"""Get job status service.

Handles job status retrieval.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.application.dtos.job_dtos import JobResponse
from app.domain.exceptions import JobNotFoundException
from app.infrastructure.repositories.job_repository import JobRepository


class GetJobStatus:
    """Service for retrieving job status."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session.

        Args:
            db: Database session
        """
        self.repository = JobRepository(db)

    def execute(self, job_id: UUID) -> JobResponse:
        """Execute job status retrieval.

        Args:
            job_id: Job UUID to retrieve

        Returns:
            Job response with current status

        Raises:
            JobNotFoundException: If job doesn't exist
        """
        job = self.repository.get_by_id(job_id)

        if not job:
            raise JobNotFoundException(str(job_id))

        return JobResponse(
            job_id=job.id,
            status=job.status,
            created_at=job.created_at,
            completed_at=job.completed_at,
            result=job.result,
            error_message=job.error_message,
        )
