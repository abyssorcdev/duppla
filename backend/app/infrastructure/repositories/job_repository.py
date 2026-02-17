"""Job repository for data access.

Handles job persistence and retrieval operations.
"""

from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.job import Job
from app.domain.exceptions import JobNotFoundException
from app.infrastructure.database.models import JobModel


class JobRepository:
    """Repository for Job entity persistence."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, job: Job) -> Job:
        """Create a new job in database.

        Args:
            job: Job entity to persist

        Returns:
            Job entity (ID already set)
        """
        db_job = JobModel(
            id=job.id,
            document_ids=job.document_ids,
            status=job.status,
            created_at=job.created_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            result=job.result,
        )
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)

        return job

    def get_by_id(self, job_id: UUID) -> Optional[Job]:
        """Get job by ID.

        Args:
            job_id: Job UUID

        Returns:
            Job entity if found, None otherwise
        """
        db_job = self.db.query(JobModel).filter(JobModel.id == job_id).first()

        if not db_job:
            return None

        return self._to_entity(db_job)

    def update_status(self, job_id: UUID, status: str, **kwargs: Any) -> Job:
        """Update job status and related fields.

        Args:
            job_id: Job UUID
            status: New status value
            **kwargs: Additional fields to update (completed_at, error_message, result)

        Returns:
            Updated job entity

        Raises:
            JobNotFoundException: If job not found
        """
        db_job = self.db.query(JobModel).filter(JobModel.id == job_id).first()

        if not db_job:
            raise JobNotFoundException(str(job_id))

        # Update status
        db_job.status = status

        # Update optional fields
        if "completed_at" in kwargs:
            db_job.completed_at = kwargs["completed_at"]
        if "error_message" in kwargs:
            db_job.error_message = kwargs["error_message"]
        if "result" in kwargs:
            db_job.result = kwargs["result"]

        self.db.commit()
        self.db.refresh(db_job)

        return self._to_entity(db_job)

    def _to_entity(self, db_job: JobModel) -> Job:
        """Convert database model to domain entity.

        Args:
            db_job: SQLAlchemy model instance

        Returns:
            Job domain entity
        """
        return Job(
            id=db_job.id,
            document_ids=db_job.document_ids,
            status=db_job.status,
            created_at=db_job.created_at,
            completed_at=db_job.completed_at,
            error_message=db_job.error_message,
            result=db_job.result,
        )
