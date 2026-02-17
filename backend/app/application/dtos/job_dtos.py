"""Job DTOs (Data Transfer Objects).

Request and response schemas for job operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
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
