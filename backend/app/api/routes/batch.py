"""Batch processing API routes.

Endpoints for triggering batch document processing.
Draft documents are evaluated and moved to pending/rejected.
Rejected documents included in the batch are reset to draft.
"""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_process_batch_service
from app.api.middleware.jwt_auth import require_loader
from app.application.dtos.job_dtos import JobResponse, ProcessBatchRequest
from app.application.services import ProcessBatch

router = APIRouter(
    tags=["batch"],
    dependencies=[Depends(require_loader())],
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

    Behavior per document status:
    - **draft**    → evaluates business rules → moves to pending or rejected
    - **rejected** → resets to draft (user corrects and re-submits in a new batch)
    - **other**    → skipped

    Returns a job ID. Processing is asynchronous via Celery.
    Use GET /jobs/{job_id} to poll the result.
    """
    return service.execute(request)
