"""Document DTOs (Data Transfer Objects).

Request and response schemas for document operations.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.domain.entities.document.status import DocumentStatus

MAX_METADATA_KEYS = 20
MAX_AMOUNT = Decimal("999_999_999.99")


class DocumentType(str, Enum):
    """Valid document types."""

    INVOICE = "invoice"
    RECEIPT = "receipt"
    VOUCHER = "voucher"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"


class CreateDocumentRequest(BaseModel):
    """Request schema for creating a document."""

    type: DocumentType = Field(..., description=f"Document type: {[e.value for e in DocumentType]}")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Document amount (must be > 0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional document metadata")
    created_by: Optional[str] = Field(None, min_length=1, max_length=100, description="User who created the document")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v > MAX_AMOUNT:
            raise ValueError(f"Amount cannot exceed {MAX_AMOUNT}")
        return v

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if len(v) > MAX_METADATA_KEYS:
            raise ValueError(f"Metadata cannot have more than {MAX_METADATA_KEYS} keys")
        return v


class UpdateDocumentRequest(BaseModel):
    """Request schema for updating a document."""

    type: Optional[DocumentType] = Field(None, description=f"Document type: {[e.value for e in DocumentType]}")
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2, description="Document amount")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")
    user_id: str = Field(..., min_length=1, max_length=100, description="User performing the update")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v > MAX_AMOUNT:
            raise ValueError(f"Amount cannot exceed {MAX_AMOUNT}")
        return v

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is not None and len(v) > MAX_METADATA_KEYS:
            raise ValueError(f"Metadata cannot have more than {MAX_METADATA_KEYS} keys")
        return v


class UpdateStatusRequest(BaseModel):
    """Request schema for updating document status."""

    new_status: DocumentStatus = Field(
        ..., description="New status. DRAFT not allowed as target — use pending, approved or rejected"
    )
    comment: Optional[str] = Field(
        None, max_length=500, description="Rejection comment (saved to document metadata when rejecting)"
    )

    @field_validator("new_status")
    @classmethod
    def validate_new_status(cls, v: DocumentStatus) -> DocumentStatus:
        if v == DocumentStatus.DRAFT:
            raise ValueError("Cannot transition to DRAFT status")
        return v


class DocumentResponse(BaseModel):
    """Response schema for a document."""

    id: int = Field(..., description="Document ID")
    type: DocumentType = Field(..., description="Document type")
    amount: Decimal = Field(..., description="Document amount")
    status: DocumentStatus = Field(..., description="Document status")
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
