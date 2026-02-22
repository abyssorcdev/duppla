"""Document status value object.

Defines valid states and state-related validation logic.
"""

from enum import Enum


class DocumentStatus(str, Enum):
    """Valid states for a financial document.

    Workflow:
        DRAFT → PENDING → APPROVED/REJECTED → DRAFT (re-open)

    - DRAFT: Initial state, document can be edited
    - PENDING: Under review, document is read-only
    - APPROVED: Approved, truly final — cannot be changed
    - REJECTED: Rejected, but can be re-opened to DRAFT for correction
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
        """Check if a state is truly final (no outgoing transitions allowed).

        Only APPROVED is immutable. REJECTED can be re-opened to DRAFT.
        """
        return status == cls.APPROVED.value

    @classmethod
    def is_editable(cls, status: str) -> bool:
        """Check if documents in this state can be edited."""
        return status == cls.DRAFT.value
