"""Update document status service.

Handles document status transitions with state machine validation and audit logging.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.application.dtos.document_dtos import DocumentResponse, UpdateStatusRequest
from app.domain.exceptions import (
    DocumentNotFoundException,
    InvalidStateTransitionException,
)
from app.domain.state_machine import StateMachine
from app.infrastructure.repositories.audit_repository import AuditRepository
from app.infrastructure.repositories.document_repository import DocumentRepository


class UpdateStatus:
    """Service for updating document status."""

    def __init__(self, db: Session) -> None:
        """Initialize service with database session.

        Args:
            db: Database session
        """
        self.document_repository = DocumentRepository(db)
        self.audit_repository = AuditRepository(db)

    def execute(
        self,
        document_id: int,
        request: UpdateStatusRequest,
        user_id: Optional[str] = None,
    ) -> DocumentResponse:
        """Execute status update with validation and audit logging.

        Args:
            document_id: Document ID to update
            request: Status update request
            user_id: Optional user performing the action

        Returns:
            Updated document response

        Raises:
            DocumentNotFoundException: If document doesn't exist
            InvalidStateTransitionException: If transition is not allowed
        """
        document = self.document_repository.get_by_id(document_id)

        if not document:
            raise DocumentNotFoundException(document_id)

        if not StateMachine.validate_transition(document.status, request.new_status):
            raise InvalidStateTransitionException(document.status, request.new_status)

        old_status = document.status
        document.change_status(request.new_status)
        updated_document = self.document_repository.update_status(document_id, request.new_status)

        self.audit_repository.log_state_change(
            document_id=document_id,
            old_state=old_status,
            new_state=request.new_status,
            user_id=user_id,
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
