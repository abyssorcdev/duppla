"""Document entity - Financial document domain model.

Business logic for financial documents (invoices, receipts, etc).
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.domain.entities.document.status import DocumentStatus
from app.domain.exceptions import (
    DocumentNotEditableException,
    InvalidAmountException,
    InvalidStateTransitionException,
)
from app.domain.state_machine import StateMachine


AUTO_PROCESSING_AMOUNT_LIMIT = Decimal("10_000_000")
AUTO_PROCESSING_REQUIRED_METADATA: List[str] = ["client", "email"]


class Document:
    """Financial document entity.

    Represents a financial document (invoice, receipt, voucher) with
    its lifecycle management and business rules.

    Attributes:
        id: Unique identifier
        type: Document type (invoice, receipt, voucher)
        amount: Amount (must be > 0)
        status: Current state in the workflow
        created_at: Creation timestamp
        updated_at: Last update timestamp
        metadata: Additional flexible data (JSON)
        created_by: User who created the document
    """

    def __init__(
        self,
        type: str,
        amount: Decimal,
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[int] = None,
        status: str = DocumentStatus.DRAFT.value,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
    ) -> None:
        """Initialize a Document.

        Args:
            type: Document type
            amount: Document amount (must be > 0)
            metadata: Optional additional data
            id: Optional document ID (set by database)
            status: Initial state (defaults to DRAFT)
            created_at: Creation timestamp (defaults to now)
            updated_at: Update timestamp (defaults to now)
            created_by: User identifier

        Raises:
            InvalidAmountException: If amount <= 0
        """
        if amount <= 0:
            raise InvalidAmountException(amount)

        self.id = id
        self.type = type
        self.amount = amount
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.metadata = metadata or {}
        self.created_by = created_by

    def change_status(self, new_status: str) -> None:
        """Change document status with validation.

        Args:
            new_status: Desired new status

        Raises:
            InvalidStateTransitionException: If transition is not allowed
        """
        if not StateMachine.validate_transition(self.status, new_status):
            raise InvalidStateTransitionException(self.status, new_status)

        self.status = new_status
        self.updated_at = datetime.utcnow()

    def update(
        self,
        type: Optional[str] = None,
        amount: Optional[Decimal] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update document fields.

        Only allowed in DRAFT state.

        Args:
            type: New document type
            amount: New amount
            metadata: New metadata

        Raises:
            DocumentNotEditableException: If not in DRAFT state
            InvalidAmountException: If amount <= 0
        """
        if self.status != DocumentStatus.DRAFT.value:
            raise DocumentNotEditableException(self.id or 0, self.status)

        if type is not None:
            self.type = type

        if amount is not None:
            if amount <= 0:
                raise InvalidAmountException(amount)
            self.amount = amount

        if metadata is not None:
            self.metadata = metadata

        self.updated_at = datetime.utcnow()

    def evaluate_for_auto_processing(self) -> tuple[str, str | None]:
        """Determine the status this document should receive after automated batch processing.

        Business rules (evaluated in order):
        1. amount > 10,000,000 → rejected (too large for automated approval, requires manual review)
        2. Missing required metadata fields (client, email) → rejected (incomplete document)
        3. All rules pass → pending (ready for human review)

        Returns:
            Tuple of (new_status, rejection_reason_or_None)
        """
        if self.amount > AUTO_PROCESSING_AMOUNT_LIMIT:
            return DocumentStatus.REJECTED.value, "amount_exceeds_limit"

        missing_fields = [f for f in AUTO_PROCESSING_REQUIRED_METADATA if not self.metadata.get(f)]
        if missing_fields:
            return DocumentStatus.REJECTED.value, "missing_required_fields"

        return DocumentStatus.PENDING.value, None

    def can_edit(self) -> bool:
        """Check if document can be edited."""
        return DocumentStatus.is_editable(self.status)

    def is_final_state(self) -> bool:
        """Check if document is in a final state."""
        return DocumentStatus.is_final(self.status)

    def __repr__(self) -> str:
        """String representation of Document."""
        return f"Document(id={self.id}, type='{self.type}', amount={self.amount}, status='{self.status}')"
