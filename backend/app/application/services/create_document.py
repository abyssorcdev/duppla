"""Create document service.

Handles document creation with business rules validation.
"""

from sqlalchemy.orm import Session

from app.application.dtos.document_dtos import CreateDocumentRequest, DocumentResponse
from app.domain.entities.document import Document
from app.infrastructure.repositories.audit_repository import AuditRepository
from app.infrastructure.repositories.document_repository import DocumentRepository


class CreateDocument:
    """Service for creating a new document."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session.

        Args:
            db: Database session
        """
        self.repository = DocumentRepository(db)
        self.audit_repository = AuditRepository(db)

    def execute(self, request: CreateDocumentRequest) -> DocumentResponse:
        """Execute document creation.

        Args:
            request: Document creation request

        Returns:
            Created document response

        Raises:
            InvalidAmountException: If amount <= 0 (validated by domain entity)
        """
        document = Document(
            type=request.type,
            amount=request.amount,
            metadata=request.metadata,
            created_by=request.created_by,
        )

        created_document = self.repository.create(document)

        self.audit_repository.log_created(
            table_name="documents",
            record_id=str(created_document.id),
            summary=f"type={created_document.type}, amount={created_document.amount}",
            user_id=request.created_by,
        )

        return DocumentResponse(
            id=created_document.id,
            type=created_document.type,
            amount=created_document.amount,
            status=created_document.status,
            created_at=created_document.created_at,
            updated_at=created_document.updated_at,
            metadata=created_document.metadata,
            created_by=created_document.created_by,
        )
