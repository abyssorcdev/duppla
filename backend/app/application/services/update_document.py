"""Update document service.

Handles document field updates with business rules validation.
"""

from sqlalchemy.orm import Session

from app.application.dtos.document_dtos import DocumentResponse, UpdateDocumentRequest
from app.domain.exceptions import DocumentNotFoundException
from app.infrastructure.repositories.audit_repository import AuditRepository
from app.infrastructure.repositories.document_repository import DocumentRepository


class UpdateDocument:
    """Service for updating document fields."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session.

        Args:
            db: Database session
        """
        self.repository = DocumentRepository(db)
        self.audit_repository = AuditRepository(db)

    def execute(self, document_id: int, request: UpdateDocumentRequest) -> DocumentResponse:
        """Execute document update.

        Args:
            document_id: Document ID to update
            request: Update request with new field values

        Returns:
            Updated document response

        Raises:
            DocumentNotFoundException: If document doesn't exist
            DocumentNotEditableException: If document is not in DRAFT status
            InvalidAmountException: If amount <= 0
        """
        document = self.repository.get_by_id(document_id)

        if not document:
            raise DocumentNotFoundException(document_id)

        document.update(
            type=request.type,
            amount=request.amount,
            metadata=request.metadata,
        )

        update_mapping = {
            "type": request.type,
            "amount": request.amount,
            "metadata": request.metadata,
        }

        update_data = {key: value for key, value in update_mapping.items() if value is not None}
        updated_document = self.repository.update(document_id, update_data)

        self.audit_repository.log_action(
            document_id=document_id,
            action="updated",
            old_value=str({k: getattr(document, k, None) for k in update_data}),
            new_value=str(update_data),
            user_id=request.user_id,
        )

        return DocumentResponse(
            id=updated_document.id,
            type=updated_document.type,
            amount=updated_document.amount,
            status=updated_document.status,
            created_at=updated_document.created_at,
            updated_at=updated_document.updated_at,
            metadata=updated_document.metadata,
            created_by=updated_document.created_by,
        )
