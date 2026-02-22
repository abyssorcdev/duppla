"""List jobs service.

Handles paginated retrieval of all jobs.
"""

import math
from typing import Optional

from sqlalchemy.orm import Session

from app.application.dtos.job_dtos import JobListResponse, JobResponse
from app.infrastructure.repositories.job_repository import JobRepository


class ListJobs:
    """Service for listing jobs with pagination."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session.

        Args:
            db: Database session
        """
        self.repository = JobRepository(db)

    def execute(
        self,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
    ) -> JobListResponse:
        """Execute paginated job listing.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            status: Optional status filter

        Returns:
            Paginated job list response
        """
        skip = (page - 1) * page_size
        jobs, total = self.repository.list_all(status=status, skip=skip, limit=page_size)

        items = [
            JobResponse(
                job_id=job.id,
                status=job.status,
                created_at=job.created_at,
                completed_at=job.completed_at,
                result=job.result,
                error_message=job.error_message,
            )
            for job in jobs
        ]

        return JobListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=max(1, math.ceil(total / page_size)),
        )
