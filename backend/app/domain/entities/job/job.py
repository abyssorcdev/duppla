"""Job entity - Batch processing job domain model.

Business logic for async batch processing jobs.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.domain.entities.job.status import JobStatus


class Job:
    """Batch processing job entity.

    Represents an async job that processes multiple documents.

    Attributes:
        id: Unique job identifier (UUID)
        document_ids: List of document IDs to process
        status: Current job status
        created_at: Job creation timestamp
        completed_at: Job completion timestamp (null if not completed)
        error_message: Error message if job failed
        result: Processing result details (JSON)
    """

    def __init__(
        self,
        document_ids: List[int],
        id: Optional[UUID] = None,
        status: str = JobStatus.PENDING.value,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        error_message: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a Job.

        Args:
            document_ids: List of document IDs to process
            id: Optional job ID (auto-generated if not provided)
            status: Initial status (defaults to PENDING)
            created_at: Creation timestamp (defaults to now)
            completed_at: Completion timestamp
            error_message: Error message if failed
            result: Processing result data
        """
        self.id = id or uuid4()
        self.document_ids = document_ids
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.completed_at = completed_at
        self.error_message = error_message
        self.result = result

    def start_processing(self) -> None:
        """Mark job as being processed."""
        self.status = JobStatus.PROCESSING.value

    def complete(self, result: Dict[str, Any]) -> None:
        """Mark job as completed successfully.

        Args:
            result: Processing result with details
        """
        self.status = JobStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        self.result = result
        self.error_message = None

    def fail(self, error_message: str) -> None:
        """Mark job as failed.

        Args:
            error_message: Description of the failure
        """
        self.status = JobStatus.FAILED.value
        self.completed_at = datetime.utcnow()
        self.error_message = error_message

    def is_completed(self) -> bool:
        """Check if job has finished (successfully or with failure)."""
        return self.status in [JobStatus.COMPLETED.value, JobStatus.FAILED.value]

    def is_processing(self) -> bool:
        """Check if job is currently being processed."""
        return self.status == JobStatus.PROCESSING.value

    def __repr__(self) -> str:
        """String representation of Job."""
        return f"Job(id={self.id}, status='{self.status}', docs={len(self.document_ids)})"
