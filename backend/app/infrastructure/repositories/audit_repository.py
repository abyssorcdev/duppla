"""Audit log repository for tracking document actions.

Handles audit log persistence operations for all document lifecycle events.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.infrastructure.database.models import AuditLogModel


class AuditRepository:
    """Repository for audit log persistence.

    Supports logging various document actions:
    - created: Document creation
    - updated: Document field updates
    - deleted: Document deletion
    - state_change: Document status transitions
    """

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def log_action(
        self,
        document_id: int,
        action: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Log a document action.

        Args:
            document_id: Document ID
            action: Action performed (created, updated, deleted, state_change, field_updated)
            old_value: Previous value (optional, any field value as text)
            new_value: New value (optional, any field value as text)
            user_id: Optional user identifier

        Example:
            ```python
            # Log document creation
            audit_repo.log_action(doc_id, "created", user_id="user123")

            # Log state change
            audit_repo.log_action(
                doc_id,
                "state_change",
                old_value="draft",
                new_value="pending",
                user_id="user123"
            )

            # Log field update (amount)
            audit_repo.log_action(
                doc_id,
                "field_updated",
                old_value="100.50",
                new_value="200.75",
                user_id="user123"
            )

            # Log deletion
            audit_repo.log_action(doc_id, "deleted", user_id="user123")
            ```
        """
        audit_log = AuditLogModel(
            document_id=document_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            timestamp=datetime.utcnow(),
            user_id=user_id,
        )
        self.db.add(audit_log)
        self.db.commit()

    def log_state_change(
        self,
        document_id: int,
        old_state: str,
        new_state: str,
        user_id: Optional[str] = None,
    ) -> None:
        """Log a document state change (convenience method).

        Args:
            document_id: Document ID
            old_state: Previous state
            new_state: New state
            user_id: Optional user identifier
        """
        self.log_action(
            document_id=document_id,
            action="state_change",
            old_value=old_state,
            new_value=new_state,
            user_id=user_id,
        )
