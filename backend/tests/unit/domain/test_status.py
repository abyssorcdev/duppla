"""Tests for app.domain.entities.document.status.DocumentStatus."""

import unittest

from tests.common import BaseTestCase

from app.domain.entities.document.status import DocumentStatus


class DocumentStatusTestCase(BaseTestCase):
    """Global base class for ALL DocumentStatus tests."""

    def setUp(self) -> None:
        super().setUp()
        self.all_statuses = [
            DocumentStatus.DRAFT,
            DocumentStatus.PENDING,
            DocumentStatus.APPROVED,
            DocumentStatus.REJECTED,
        ]


class TestIsValid(DocumentStatusTestCase):
    """Tests for is_valid() classmethod."""

    def test_is_valid_success_draft(self) -> None:
        """
        When: 'draft' is checked
        Then: Should return True
        """
        self.assertTrue(DocumentStatus.is_valid("draft"))

    def test_is_valid_success_pending(self) -> None:
        """
        When: 'pending' is checked
        Then: Should return True
        """
        self.assertTrue(DocumentStatus.is_valid("pending"))

    def test_is_valid_success_approved(self) -> None:
        """
        When: 'approved' is checked
        Then: Should return True
        """
        self.assertTrue(DocumentStatus.is_valid("approved"))

    def test_is_valid_success_rejected(self) -> None:
        """
        When: 'rejected' is checked
        Then: Should return True
        """
        self.assertTrue(DocumentStatus.is_valid("rejected"))

    def test_is_valid_error_unknown_status(self) -> None:
        """
        When: An unknown status is checked
        Then: Should return False
        """
        self.assertFalse(DocumentStatus.is_valid("cancelled"))

    def test_is_valid_error_empty_string(self) -> None:
        """
        When: Empty string is checked
        Then: Should return False
        """
        self.assertFalse(DocumentStatus.is_valid(""))

    def test_is_valid_error_case_sensitive(self) -> None:
        """
        When: Uppercase status is checked
        Then: Should return False (values are lowercase)
        """
        self.assertFalse(DocumentStatus.is_valid("DRAFT"))


class TestIsFinal(DocumentStatusTestCase):
    """Tests for is_final() classmethod."""

    def test_is_final_success_approved(self) -> None:
        """
        When: 'approved' is checked
        Then: Should return True (only truly final state)
        """
        self.assertTrue(DocumentStatus.is_final("approved"))

    def test_is_final_error_draft(self) -> None:
        """
        When: 'draft' is checked
        Then: Should return False
        """
        self.assertFalse(DocumentStatus.is_final("draft"))

    def test_is_final_error_pending(self) -> None:
        """
        When: 'pending' is checked
        Then: Should return False
        """
        self.assertFalse(DocumentStatus.is_final("pending"))

    def test_is_final_error_rejected(self) -> None:
        """
        When: 'rejected' is checked
        Then: Should return False (can be re-opened)
        """
        self.assertFalse(DocumentStatus.is_final("rejected"))

    def test_is_final_error_unknown(self) -> None:
        """
        When: Unknown status is checked
        Then: Should return False
        """
        self.assertFalse(DocumentStatus.is_final("unknown"))


class TestIsEditable(DocumentStatusTestCase):
    """Tests for is_editable() classmethod."""

    def test_is_editable_success_draft(self) -> None:
        """
        When: 'draft' is checked
        Then: Should return True (only editable state)
        """
        self.assertTrue(DocumentStatus.is_editable("draft"))

    def test_is_editable_error_pending(self) -> None:
        """
        When: 'pending' is checked
        Then: Should return False
        """
        self.assertFalse(DocumentStatus.is_editable("pending"))

    def test_is_editable_error_approved(self) -> None:
        """
        When: 'approved' is checked
        Then: Should return False
        """
        self.assertFalse(DocumentStatus.is_editable("approved"))

    def test_is_editable_error_rejected(self) -> None:
        """
        When: 'rejected' is checked
        Then: Should return False
        """
        self.assertFalse(DocumentStatus.is_editable("rejected"))

    def test_is_editable_error_unknown(self) -> None:
        """
        When: Unknown status is checked
        Then: Should return False
        """
        self.assertFalse(DocumentStatus.is_editable("unknown"))


class TestEnumValues(DocumentStatusTestCase):
    """Tests for enum values and string behavior."""

    def test_enum_values_all_present(self) -> None:
        """
        When: Checking all enum members
        Then: Should have exactly 4 statuses
        """
        self.assertEqual(len(DocumentStatus), 4)

    def test_enum_values_string_comparison(self) -> None:
        """
        When: Comparing enum to string
        Then: Should be equal (str mixin)
        """
        self.assertEqual(DocumentStatus.DRAFT, "draft")
        self.assertEqual(DocumentStatus.PENDING, "pending")
        self.assertEqual(DocumentStatus.APPROVED, "approved")
        self.assertEqual(DocumentStatus.REJECTED, "rejected")

    def test_enum_value_attribute(self) -> None:
        """
        When: Accessing .value
        Then: Should return the lowercase string
        """
        self.assertEqual(DocumentStatus.DRAFT.value, "draft")
        self.assertEqual(DocumentStatus.APPROVED.value, "approved")
