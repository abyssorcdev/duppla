"""Jobs API routes.

Endpoints for listing and querying batch processing jobs.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_get_job_status_service, get_list_jobs_service
from app.api.middleware.jwt_auth import require_any_active_role
from app.application.dtos.job_dtos import JobListResponse, JobResponse
from app.application.services import GetJobStatus, ListJobs

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    dependencies=[Depends(require_any_active_role())],
)


@router.get(
    "",
    response_model=JobListResponse,
    summary="List all jobs",
)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (pending, processing, completed, failed)"),
    service: ListJobs = Depends(get_list_jobs_service),
) -> JobListResponse:
    """List all batch processing jobs with optional filters.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **status**: Optional filter by job status
    """
    return service.execute(page=page, page_size=page_size, status=status)


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job status",
)
async def get_job_status(
    job_id: UUID,
    service: GetJobStatus = Depends(get_get_job_status_service),
) -> JobResponse:
    """Get the status of a batch processing job.

    - **job_id**: Job UUID to query

    Returns job details including status, timestamps and results.
    """
    return service.execute(job_id)
