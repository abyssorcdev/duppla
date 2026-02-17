"""Get document service.

Handles document retrieval by ID.
"""

from sqlalchemy.orm import Session

from app.application.dtos.document_dtos import DocumentResponse
from app.domain.exceptions import DocumentNotFoundException
from app.infrastructure.repositories.document_repository import DocumentRepository


class GetDocument:
    """Service for retrieving a document by ID."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session.

        Args:
            db: Database session
        """
        self.repository = DocumentRepository(db)

    def execute(self, document_id: int) -> DocumentResponse:
        """Execute document retrieval.

        Args:
            document_id: Document ID to retrieve

        Returns:
            Document response

        Raises:
            DocumentNotFoundException: If document doesn't exist
        """
        document = self.repository.get_by_id(document_id)

        if not document:
            raise DocumentNotFoundException(document_id)

        return DocumentResponse(
            id=document.id,
            type=document.type,
            amount=document.amount,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at,
            metadata=document.metadata,
            created_by=document.created_by,
        )
