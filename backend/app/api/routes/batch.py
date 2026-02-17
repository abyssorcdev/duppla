"""Batch processing and job API routes.

Endpoints for batch operations and job status.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_get_job_status_service,
    get_process_batch_service,
)
from app.api.middleware.auth import verify_api_key
from app.application.dtos.job_dtos import JobResponse, ProcessBatchRequest
from app.application.services import GetJobStatus, ProcessBatch

router = APIRouter(
    tags=["batch", "jobs"],
    dependencies=[Depends(verify_api_key)],
)


@router.post(
    "/documents/batch/process",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Process documents in batch",
)
async def process_batch(
    request: ProcessBatchRequest,
    service: ProcessBatch = Depends(get_process_batch_service),
) -> JobResponse:
    """Create a batch processing job for multiple documents.

    - **document_ids**: List of document IDs to process

    Returns a job ID with status 'pending'.
    The actual processing happens asynchronously via Celery.
    Use GET /jobs/{job_id} to check the job status.
    """
    return service.execute(request)


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    summary="Get job status",
)
async def get_job_status(
    job_id: UUID,
    service: GetJobStatus = Depends(get_get_job_status_service),
) -> JobResponse:
    """Get the status of a batch processing job.

    - **job_id**: Job UUID to query

    Returns job details including:
    - status: pending, processing, completed, or failed
    - created_at: Job creation timestamp
    - completed_at: Completion timestamp (if finished)
    - result: Processing results (if completed)
    - error_message: Error details (if failed)
    """
    return service.execute(job_id)
