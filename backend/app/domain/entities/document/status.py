"""Document status value object.

Defines valid states and state-related validation logic.
"""

from enum import Enum


class DocumentStatus(str, Enum):
    """Valid states for a financial document.

    Workflow:
        DRAFT → PENDING → APPROVED/REJECTED

    - DRAFT: Initial state, document can be edited
    - PENDING: Under review, document is read-only
    - APPROVED: Approved, final immutable state
    - REJECTED: Rejected, final immutable state
    """

    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    @classmethod
    def is_valid(cls, status: str) -> bool:
        """Check if a state is valid."""
        return status in [e.value for e in cls]

    @classmethod
    def is_final(cls, status: str) -> bool:
        """Check if a state is final (cannot transition from it)."""
        return status in [cls.APPROVED.value, cls.REJECTED.value]

    @classmethod
    def is_editable(cls, status: str) -> bool:
        """Check if documents in this state can be edited."""
        return status == cls.DRAFT.value
