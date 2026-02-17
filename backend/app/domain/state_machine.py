"""State machine for document state transitions.

Validates state transitions according to business rules.
"""

from typing import ClassVar, Dict, List

from app.domain.entities.document.status import DocumentStatus


class StateMachine:
    """State machine for validating document state transitions.

    Valid transitions:
        DRAFT → PENDING
        PENDING → APPROVED
        PENDING → REJECTED

    Invalid transitions (examples):
        DRAFT → APPROVED (must go through PENDING)
        APPROVED → * (final state, immutable)
        REJECTED → * (final state, immutable)
    """

    # Transition matrix: current_state → [allowed_states]
    TRANSITIONS: ClassVar[Dict[str, List[str]]] = {
        DocumentStatus.DRAFT.value: [DocumentStatus.PENDING.value],
        DocumentStatus.PENDING.value: [
            DocumentStatus.APPROVED.value,
            DocumentStatus.REJECTED.value,
        ],
        DocumentStatus.APPROVED.value: [],  # Final state, no transitions
        DocumentStatus.REJECTED.value: [],  # Final state, no transitions
    }

    @classmethod
    def validate_transition(cls, current_state: str, new_state: str) -> bool:
        """Validate if transition from current_state to new_state is allowed.

        Args:
            current_state: Current state of the document
            new_state: Desired new state

        Returns:
            True if transition is valid, False otherwise
        """
        if current_state not in cls.TRANSITIONS:
            return False

        allowed_states = cls.TRANSITIONS[current_state]
        return new_state in allowed_states

    @classmethod
    def get_valid_next_states(cls, current_state: str) -> List[str]:
        """Get list of valid next states from current state.

        Args:
            current_state: Current state of the document

        Returns:
            List of valid next states
        """
        return cls.TRANSITIONS.get(current_state, [])

    @classmethod
    def is_final_state(cls, state: str) -> bool:
        """Check if a state is final (no outgoing transitions).

        Args:
            state: State to check

        Returns:
            True if state is final (APPROVED or REJECTED)
        """
        return len(cls.TRANSITIONS.get(state, [])) == 0
