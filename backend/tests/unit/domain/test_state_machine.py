"""Tests for app.domain.state_machine.StateMachine."""

import unittest

from tests.common import BaseTestCase

from app.domain.entities.document.status import DocumentStatus
from app.domain.state_machine import StateMachine


class StateMachineTestCase(BaseTestCase):
    """Global base class for ALL StateMachine tests."""

    def setUp(self) -> None:
        super().setUp()
        self.draft = DocumentStatus.DRAFT.value
        self.pending = DocumentStatus.PENDING.value
        self.approved = DocumentStatus.APPROVED.value
        self.rejected = DocumentStatus.REJECTED.value


class TestValidateTransition(StateMachineTestCase):
    """Tests for validate_transition()."""

    def test_validate_transition_success_draft_to_pending(self) -> None:
        """
        When: Transition from DRAFT to PENDING
        Then: Should return True
        """
        result = StateMachine.validate_transition(self.draft, self.pending)
        self.assertTrue(result)

    def test_validate_transition_success_draft_to_rejected(self) -> None:
        """
        When: Transition from DRAFT to REJECTED
        Then: Should return True (direct rejection by worker)
        """
        result = StateMachine.validate_transition(self.draft, self.rejected)
        self.assertTrue(result)

    def test_validate_transition_success_pending_to_approved(self) -> None:
        """
        When: Transition from PENDING to APPROVED
        Then: Should return True
        """
        result = StateMachine.validate_transition(self.pending, self.approved)
        self.assertTrue(result)

    def test_validate_transition_success_pending_to_rejected(self) -> None:
        """
        When: Transition from PENDING to REJECTED
        Then: Should return True
        """
        result = StateMachine.validate_transition(self.pending, self.rejected)
        self.assertTrue(result)

    def test_validate_transition_success_rejected_to_draft(self) -> None:
        """
        When: Transition from REJECTED to DRAFT
        Then: Should return True (re-open for correction)
        """
        result = StateMachine.validate_transition(self.rejected, self.draft)
        self.assertTrue(result)

    def test_validate_transition_error_draft_to_approved(self) -> None:
        """
        When: Transition from DRAFT directly to APPROVED
        Then: Should return False (must go through PENDING)
        """
        result = StateMachine.validate_transition(self.draft, self.approved)
        self.assertFalse(result)

    def test_validate_transition_error_approved_to_any(self) -> None:
        """
        When: Transition from APPROVED to any state
        Then: Should return False (APPROVED is final)
        """
        for target in [self.draft, self.pending, self.rejected]:
            with self.subTest(target=target):
                result = StateMachine.validate_transition(self.approved, target)
                self.assertFalse(result)

    def test_validate_transition_error_unknown_state(self) -> None:
        """
        When: Current state is unknown
        Then: Should return False
        """
        result = StateMachine.validate_transition("unknown", self.pending)
        self.assertFalse(result)

    def test_validate_transition_error_same_state(self) -> None:
        """
        When: Transition to the same state
        Then: Should return False
        """
        for state in [self.draft, self.pending, self.approved, self.rejected]:
            with self.subTest(state=state):
                result = StateMachine.validate_transition(state, state)
                self.assertFalse(result)


class TestGetValidNextStates(StateMachineTestCase):
    """Tests for get_valid_next_states()."""

    def test_get_valid_next_states_success_from_draft(self) -> None:
        """
        When: Current state is DRAFT
        Then: Should return [PENDING, REJECTED]
        """
        result = StateMachine.get_valid_next_states(self.draft)
        self.assertCountEqual(result, [self.pending, self.rejected])

    def test_get_valid_next_states_success_from_pending(self) -> None:
        """
        When: Current state is PENDING
        Then: Should return [APPROVED, REJECTED]
        """
        result = StateMachine.get_valid_next_states(self.pending)
        self.assertCountEqual(result, [self.approved, self.rejected])

    def test_get_valid_next_states_success_from_approved(self) -> None:
        """
        When: Current state is APPROVED
        Then: Should return empty list (final state)
        """
        result = StateMachine.get_valid_next_states(self.approved)
        self.assertEqual(result, [])

    def test_get_valid_next_states_success_from_rejected(self) -> None:
        """
        When: Current state is REJECTED
        Then: Should return [DRAFT]
        """
        result = StateMachine.get_valid_next_states(self.rejected)
        self.assertEqual(result, [self.draft])

    def test_get_valid_next_states_error_unknown_state(self) -> None:
        """
        When: State is unknown
        Then: Should return empty list
        """
        result = StateMachine.get_valid_next_states("unknown")
        self.assertEqual(result, [])


class TestIsUnderScoreFinalUnderScoreState(StateMachineTestCase):
    """Tests for is_final_state()."""

    def test_is_final_state_success_approved(self) -> None:
        """
        When: State is APPROVED
        Then: Should return True
        """
        self.assertTrue(StateMachine.is_final_state(self.approved))

    def test_is_final_state_error_draft(self) -> None:
        """
        When: State is DRAFT
        Then: Should return False
        """
        self.assertFalse(StateMachine.is_final_state(self.draft))

    def test_is_final_state_error_pending(self) -> None:
        """
        When: State is PENDING
        Then: Should return False
        """
        self.assertFalse(StateMachine.is_final_state(self.pending))

    def test_is_final_state_error_rejected(self) -> None:
        """
        When: State is REJECTED (can go back to DRAFT)
        Then: Should return False
        """
        self.assertFalse(StateMachine.is_final_state(self.rejected))
