"""Job DTOs (Data Transfer Objects).

Request and response schemas for job operations and webhook callbacks.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProcessBatchRequest(BaseModel):
    """Request schema for processing a batch of documents."""

    document_ids: List[int] = Field(..., min_length=1, description="List of document IDs to process")


class JobResponse(BaseModel):
    """Response schema for a job."""

    job_id: UUID = Field(..., description="Job unique identifier")
    status: str = Field(..., description="Job status (pending, processing, completed, failed)")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    result: Optional[Dict[str, Any]] = Field(None, description="Job result details (if completed)")
    error_message: Optional[str] = Field(None, description="Error message (if failed)")

    class Config:
        """Pydantic config."""

        from_attributes = True


class WebhookDocumentDetail(BaseModel):
    """Individual document result in webhook payload."""

    document_id: int = Field(..., description="Document ID")
    status: Literal["success", "failed"] = Field(..., description="Processing result")
    error: Optional[str] = Field(None, description="Error message if failed")


class WebhookJobResult(BaseModel):
    """Job result details in webhook payload."""

    total: int = Field(..., description="Total documents in batch")
    processed: int = Field(..., description="Successfully processed count")
    failed: int = Field(..., description="Failed count")
    details: List[WebhookDocumentDetail] = Field(..., description="Per-document results")


class JobCompletedWebhookPayload(BaseModel):
    """Payload received from Celery when a batch job completes."""

    job_id: str = Field(..., description="Job UUID")
    status: Literal["completed", "failed"] = Field(..., description="Final job status")
    document_ids: List[int] = Field(..., description="All document IDs in the batch")
    result: WebhookJobResult = Field(..., description="Processing result details")
    error_message: Optional[str] = Field(None, description="Critical error if job failed entirely")
