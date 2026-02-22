"""Tests for app.domain.entities.document.document.Document."""

import unittest
from decimal import Decimal

from tests.common import BaseTestCase

from app.domain.entities.document.document import Document
from app.domain.entities.document.status import DocumentStatus
from app.domain.exceptions import (
    DocumentNotEditableException,
    InvalidAmountException,
    InvalidStateTransitionException,
)


class DocumentTestCase(BaseTestCase):
    """Global base class for ALL Document tests."""

    def setUp(self) -> None:
        super().setUp()
        self.valid_type = self.fake.random_element(["invoice", "receipt", "voucher"])
        self.valid_amount = Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True)))
        self.valid_metadata = {"client": self.fake.company(), "email": self.fake.company_email()}

    def get_instance(self, **overrides: object) -> Document:
        """Factory method for creating Document instances."""
        defaults = {
            "type": self.valid_type,
            "amount": self.valid_amount,
            "metadata": self.valid_metadata.copy(),
        }
        defaults.update(overrides)
        return Document(**defaults)


class TestUnderScoreUnderScoreInit(DocumentTestCase):
    """Tests for __init__()."""

    def test_init_success_valid_params(self) -> None:
        """
        When: Document is created with valid parameters
        Then: Should set all attributes correctly
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        created_by = self.fake.email()
        doc = self.get_instance(id=doc_id, created_by=created_by)

        self.assertEqual(doc.id, doc_id)
        self.assertEqual(doc.type, self.valid_type)
        self.assertEqual(doc.amount, self.valid_amount)
        self.assertEqual(doc.status, DocumentStatus.DRAFT.value)
        self.assertEqual(doc.metadata, self.valid_metadata)
        self.assertEqual(doc.created_by, created_by)
        self.assertIsNotNone(doc.created_at)
        self.assertIsNotNone(doc.updated_at)

    def test_init_success_defaults(self) -> None:
        """
        When: Document is created with only required parameters
        Then: Should use default values for optional fields
        """
        amount = Decimal(str(self.fake.pydecimal(min_value=1, max_value=9999, right_digits=2, positive=True)))
        doc = Document(type="receipt", amount=amount)

        self.assertIsNone(doc.id)
        self.assertEqual(doc.status, DocumentStatus.DRAFT.value)
        self.assertEqual(doc.metadata, {})
        self.assertIsNone(doc.created_by)

    def test_init_error_zero_amount(self) -> None:
        """
        When: Amount is zero
        Then: Should raise InvalidAmountException
        """
        with self.assertRaises(InvalidAmountException):
            Document(type="invoice", amount=Decimal("0"))

    def test_init_error_negative_amount(self) -> None:
        """
        When: Amount is negative
        Then: Should raise InvalidAmountException
        """
        with self.assertRaises(InvalidAmountException):
            Document(type="invoice", amount=Decimal("-100"))


class TestChangeStatus(DocumentTestCase):
    """Tests for change_status()."""

    def test_change_status_success_draft_to_pending(self) -> None:
        """
        When: Changing from DRAFT to PENDING
        Then: Should update status and updated_at
        """
        doc = self.get_instance()
        old_updated_at = doc.updated_at

        doc.change_status(DocumentStatus.PENDING.value)

        self.assertEqual(doc.status, DocumentStatus.PENDING.value)
        self.assertGreaterEqual(doc.updated_at, old_updated_at)

    def test_change_status_success_full_approval_flow(self) -> None:
        """
        When: Document goes through DRAFT → PENDING → APPROVED
        Then: Should reach APPROVED status
        """
        doc = self.get_instance()
        doc.change_status(DocumentStatus.PENDING.value)
        doc.change_status(DocumentStatus.APPROVED.value)

        self.assertEqual(doc.status, DocumentStatus.APPROVED.value)

    def test_change_status_error_invalid_transition(self) -> None:
        """
        When: Attempting DRAFT → APPROVED (skipping PENDING)
        Then: Should raise InvalidStateTransitionException
        """
        doc = self.get_instance()

        with self.assertRaises(InvalidStateTransitionException) as ctx:
            doc.change_status(DocumentStatus.APPROVED.value)

        self.assertIn("draft", ctx.exception.message)
        self.assertIn("approved", ctx.exception.message)

    def test_change_status_error_from_approved(self) -> None:
        """
        When: Trying to change status from APPROVED
        Then: Should raise InvalidStateTransitionException (final state)
        """
        doc = self.get_instance()
        doc.change_status(DocumentStatus.PENDING.value)
        doc.change_status(DocumentStatus.APPROVED.value)

        with self.assertRaises(InvalidStateTransitionException):
            doc.change_status(DocumentStatus.DRAFT.value)


class TestUpdate(DocumentTestCase):
    """Tests for update()."""

    def test_update_success_all_fields(self) -> None:
        """
        When: Updating all fields in DRAFT state
        Then: Should update type, amount, and metadata
        """
        doc = self.get_instance()

        new_type = self.fake.random_element(["receipt", "voucher"])
        new_amount = Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True)))
        new_metadata = {"client": self.fake.company()}
        doc.update(type=new_type, amount=new_amount, metadata=new_metadata)

        self.assertEqual(doc.type, new_type)
        self.assertEqual(doc.amount, new_amount)
        self.assertEqual(doc.metadata, new_metadata)

    def test_update_success_partial_fields(self) -> None:
        """
        When: Updating only the amount
        Then: Should update amount and keep other fields unchanged
        """
        doc = self.get_instance()
        original_type = doc.type

        new_amount = Decimal(str(self.fake.pydecimal(min_value=1, max_value=999_999, right_digits=2, positive=True)))
        doc.update(amount=new_amount)

        self.assertEqual(doc.amount, new_amount)
        self.assertEqual(doc.type, original_type)

    def test_update_error_not_in_draft(self) -> None:
        """
        When: Trying to update a document in PENDING state
        Then: Should raise DocumentNotEditableException
        """
        doc = self.get_instance()
        doc.change_status(DocumentStatus.PENDING.value)

        with self.assertRaises(DocumentNotEditableException):
            doc.update(amount=Decimal("999"))

    def test_update_error_invalid_amount(self) -> None:
        """
        When: Updating with amount <= 0
        Then: Should raise InvalidAmountException
        """
        doc = self.get_instance()

        with self.assertRaises(InvalidAmountException):
            doc.update(amount=Decimal("-50"))


class TestEvaluateForAutoProcessing(DocumentTestCase):
    """Tests for evaluate_for_auto_processing()."""

    def test_evaluate_success_valid_document(self) -> None:
        """
        When: Document has valid amount and all required metadata
        Then: Should return PENDING status with no rejection reason
        """
        doc = self.get_instance()

        status, reason = doc.evaluate_for_auto_processing()

        self.assertEqual(status, DocumentStatus.PENDING.value)
        self.assertIsNone(reason)

    def test_evaluate_rejected_amount_exceeds_limit(self) -> None:
        """
        When: Amount exceeds 10,000,000
        Then: Should return REJECTED with 'amount_exceeds_limit'
        """
        doc = self.get_instance(amount=Decimal("10_000_001"))

        status, reason = doc.evaluate_for_auto_processing()

        self.assertEqual(status, DocumentStatus.REJECTED.value)
        self.assertEqual(reason, "amount_exceeds_limit")

    def test_evaluate_rejected_missing_metadata(self) -> None:
        """
        When: Required metadata fields are missing
        Then: Should return REJECTED with 'missing_required_fields'
        """
        doc = self.get_instance(metadata={})

        status, reason = doc.evaluate_for_auto_processing()

        self.assertEqual(status, DocumentStatus.REJECTED.value)
        self.assertEqual(reason, "missing_required_fields")

    def test_evaluate_rejected_partial_metadata(self) -> None:
        """
        When: Only some required metadata fields are present
        Then: Should return REJECTED
        """
        doc = self.get_instance(metadata={"client": self.fake.company()})

        status, reason = doc.evaluate_for_auto_processing()

        self.assertEqual(status, DocumentStatus.REJECTED.value)
        self.assertEqual(reason, "missing_required_fields")

    def test_evaluate_success_at_exact_limit(self) -> None:
        """
        When: Amount is exactly 10,000,000 (the limit)
        Then: Should return PENDING (limit is not exceeded)
        """
        doc = self.get_instance(
            amount=Decimal("10_000_000"),
            metadata=self.valid_metadata,
        )

        status, reason = doc.evaluate_for_auto_processing()

        self.assertEqual(status, DocumentStatus.PENDING.value)
        self.assertIsNone(reason)


class TestCanEdit(DocumentTestCase):
    """Tests for can_edit()."""

    def test_can_edit_success_draft(self) -> None:
        """
        When: Document is in DRAFT state
        Then: Should return True
        """
        doc = self.get_instance()
        self.assertTrue(doc.can_edit())

    def test_can_edit_error_pending(self) -> None:
        """
        When: Document is in PENDING state
        Then: Should return False
        """
        doc = self.get_instance()
        doc.change_status(DocumentStatus.PENDING.value)
        self.assertFalse(doc.can_edit())


class TestIsUnderScoreFinalUnderScoreState(DocumentTestCase):
    """Tests for is_final_state()."""

    def test_is_final_state_success_approved(self) -> None:
        """
        When: Document is APPROVED
        Then: Should return True
        """
        doc = self.get_instance()
        doc.change_status(DocumentStatus.PENDING.value)
        doc.change_status(DocumentStatus.APPROVED.value)
        self.assertTrue(doc.is_final_state())

    def test_is_final_state_error_draft(self) -> None:
        """
        When: Document is in DRAFT
        Then: Should return False
        """
        doc = self.get_instance()
        self.assertFalse(doc.is_final_state())

    def test_is_final_state_error_rejected(self) -> None:
        """
        When: Document is REJECTED
        Then: Should return False (can be re-opened)
        """
        doc = self.get_instance()
        doc.change_status(DocumentStatus.PENDING.value)
        doc.change_status(DocumentStatus.REJECTED.value)
        self.assertFalse(doc.is_final_state())


class TestUnderScoreUnderScoreRepr(DocumentTestCase):
    """Tests for __repr__()."""

    def test_repr_success_format(self) -> None:
        doc = self.get_instance()
        result = repr(doc)
        self.assertIn("Document(", result)
        self.assertIn(f"type='{doc.type}'", result)
        self.assertIn(f"status='{doc.status}'", result)

    def test_repr_success_contains_amount(self) -> None:
        doc = self.get_instance()
        result = repr(doc)
        self.assertIn(str(doc.amount), result)
