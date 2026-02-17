"""Document DTOs (Data Transfer Objects).

Request and response schemas for document operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CreateDocumentRequest(BaseModel):
    """Request schema for creating a document."""

    type: str = Field(..., min_length=1, max_length=50, description="Document type")
    amount: Decimal = Field(..., gt=0, description="Document amount (must be > 0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional document metadata")
    created_by: Optional[str] = Field(None, max_length=100, description="User who created the document")


class UpdateDocumentRequest(BaseModel):
    """Request schema for updating a document."""

    type: Optional[str] = Field(None, min_length=1, max_length=50, description="Document type")
    amount: Optional[Decimal] = Field(None, gt=0, description="Document amount")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")


class UpdateStatusRequest(BaseModel):
    """Request schema for updating document status."""

    new_status: str = Field(..., description="New status for the document")


class DocumentResponse(BaseModel):
    """Response schema for a document."""

    id: int = Field(..., description="Document ID")
    type: str = Field(..., description="Document type")
    amount: Decimal = Field(..., description="Document amount")
    status: str = Field(..., description="Document status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    created_by: Optional[str] = Field(None, description="User who created the document")

    class Config:
        """Pydantic config."""

        from_attributes = True


class SearchDocumentsRequest(BaseModel):
    """Request schema for searching documents."""

    type: Optional[str] = Field(None, description="Filter by document type")
    status: Optional[str] = Field(None, description="Filter by status")
    amount_min: Optional[Decimal] = Field(None, description="Minimum amount filter")
    amount_max: Optional[Decimal] = Field(None, description="Maximum amount filter")
    created_from: Optional[datetime] = Field(None, description="Filter documents created from this date")
    created_to: Optional[datetime] = Field(None, description="Filter documents created until this date")
    page: int = Field(1, ge=1, description="Page number (starts at 1)")
    page_size: int = Field(50, ge=1, le=100, description="Number of items per page (max 100)")


class PaginatedDocumentsResponse(BaseModel):
    """Response schema for paginated documents."""

    items: List[DocumentResponse] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents matching filters")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
