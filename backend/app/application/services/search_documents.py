"""Search documents service.

Handles document search with filters and pagination.
"""

from math import ceil

from sqlalchemy.orm import Session

from app.application.dtos.document_dtos import (
    DocumentResponse,
    PaginatedDocumentsResponse,
    SearchDocumentsRequest,
)
from app.infrastructure.repositories.document_repository import DocumentRepository


class SearchDocuments:
    """Service for searching documents with filters and pagination."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session.

        Args:
            db: Database session
        """
        self.repository = DocumentRepository(db)

    def execute(self, request: SearchDocumentsRequest) -> PaginatedDocumentsResponse:
        """Execute document search.

        Args:
            request: Search request with filters and pagination

        Returns:
            Paginated documents response
        """
        filter_mapping = {
            "type": request.type,
            "status": request.status,
            "amount_min": request.amount_min,
            "amount_max": request.amount_max,
            "created_from": request.created_from,
            "created_to": request.created_to,
        }
        filters = {key: value for key, value in filter_mapping.items() if value is not None}
        skip = (request.page - 1) * request.page_size

        documents, total = self.repository.search(filters=filters, skip=skip, limit=request.page_size)
        total_pages = ceil(total / request.page_size) if total > 0 else 0

        items = [
            DocumentResponse(
                id=doc.id,
                type=doc.type,
                amount=doc.amount,
                status=doc.status,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                metadata=doc.metadata,
                created_by=doc.created_by,
            )
            for doc in documents
        ]

        return PaginatedDocumentsResponse(
            items=items,
            total=total,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages,
        )
