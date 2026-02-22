"""Tests for app.domain.exceptions."""

import unittest

from tests.common import BaseTestCase

from app.domain.exceptions import (
    DocumentNotEditableException,
    DocumentNotFoundException,
    DomainException,
    InvalidAmountException,
    InvalidStateTransitionException,
    JobNotFoundException,
)


class DomainExceptionsTestCase(BaseTestCase):
    """Global base class for ALL domain exception tests."""

    pass


class TestDomainException(DomainExceptionsTestCase):
    """Tests for DomainException base class."""

    def test_domain_exception_success_message(self) -> None:
        """
        When: DomainException is created with a message
        Then: Should store message correctly
        """
        msg = self.fake.sentence()
        exc = DomainException(msg)
        self.assertEqual(exc.message, msg)

    def test_domain_exception_success_str_representation(self) -> None:
        """
        When: Converting exception to string
        Then: Should return the message
        """
        msg = self.fake.sentence()
        exc = DomainException(msg)
        self.assertEqual(str(exc), msg)

    def test_domain_exception_success_is_exception(self) -> None:
        """
        When: DomainException is created
        Then: Should be an instance of Exception
        """
        exc = DomainException(self.fake.sentence())
        self.assertIsInstance(exc, Exception)


class TestInvalidStateTransitionException(DomainExceptionsTestCase):
    """Tests for InvalidStateTransitionException."""

    def test_invalid_state_transition_success_message_format(self) -> None:
        """
        When: Created with current and new state
        Then: Should include both states in message
        """
        exc = InvalidStateTransitionException("draft", "approved")
        self.assertIn("draft", exc.message)
        self.assertIn("approved", exc.message)

    def test_invalid_state_transition_success_attributes(self) -> None:
        """
        When: Created with current and new state
        Then: Should store both as attributes
        """
        exc = InvalidStateTransitionException("pending", "draft")
        self.assertEqual(exc.current_state, "pending")
        self.assertEqual(exc.new_state, "draft")

    def test_invalid_state_transition_success_inherits_domain(self) -> None:
        """
        When: Created
        Then: Should be a DomainException
        """
        exc = InvalidStateTransitionException("a", "b")
        self.assertIsInstance(exc, DomainException)

    def test_invalid_state_transition_success_can_be_caught(self) -> None:
        """
        When: Raised and caught
        Then: Should be catchable as DomainException
        """
        with self.assertRaises(DomainException):
            raise InvalidStateTransitionException("draft", "approved")


class TestDocumentNotFoundException(DomainExceptionsTestCase):
    """Tests for DocumentNotFoundException."""

    def test_document_not_found_success_message_format(self) -> None:
        """
        When: Created with document_id
        Then: Should include the ID in message
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        exc = DocumentNotFoundException(doc_id)
        self.assertIn(str(doc_id), exc.message)

    def test_document_not_found_success_attribute(self) -> None:
        """
        When: Created with document_id
        Then: Should store document_id
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        exc = DocumentNotFoundException(doc_id)
        self.assertEqual(exc.document_id, doc_id)

    def test_document_not_found_success_inherits_domain(self) -> None:
        """
        When: Created
        Then: Should be a DomainException
        """
        exc = DocumentNotFoundException(self.fake.random_int(min=1, max=99_999))
        self.assertIsInstance(exc, DomainException)


class TestJobNotFoundException(DomainExceptionsTestCase):
    """Tests for JobNotFoundException."""

    def test_job_not_found_success_message_format(self) -> None:
        """
        When: Created with job_id string
        Then: Should include the ID in message
        """
        job_id = str(self.fake.uuid4())
        exc = JobNotFoundException(job_id)
        self.assertIn(job_id, exc.message)

    def test_job_not_found_success_attribute(self) -> None:
        """
        When: Created with job_id
        Then: Should store job_id
        """
        job_id = str(self.fake.uuid4())
        exc = JobNotFoundException(job_id)
        self.assertEqual(exc.job_id, job_id)

    def test_job_not_found_success_inherits_domain(self) -> None:
        """
        When: Created
        Then: Should be a DomainException
        """
        exc = JobNotFoundException(str(self.fake.uuid4()))
        self.assertIsInstance(exc, DomainException)


class TestInvalidAmountException(DomainExceptionsTestCase):
    """Tests for InvalidAmountException."""

    def test_invalid_amount_success_message_format(self) -> None:
        """
        When: Created with amount
        Then: Should include amount in message
        """
        exc = InvalidAmountException(-100)
        self.assertIn("-100", exc.message)

    def test_invalid_amount_success_attribute(self) -> None:
        """
        When: Created with amount
        Then: Should store amount
        """
        exc = InvalidAmountException(0)
        self.assertEqual(exc.amount, 0)

    def test_invalid_amount_success_zero(self) -> None:
        """
        When: Created with zero amount
        Then: Should include message about greater than 0
        """
        exc = InvalidAmountException(0)
        self.assertIn("greater than 0", exc.message)

    def test_invalid_amount_success_inherits_domain(self) -> None:
        """
        When: Created
        Then: Should be a DomainException
        """
        exc = InvalidAmountException(-1)
        self.assertIsInstance(exc, DomainException)


class TestDocumentNotEditableException(DomainExceptionsTestCase):
    """Tests for DocumentNotEditableException."""

    def test_document_not_editable_success_message_format(self) -> None:
        """
        When: Created with document_id and current_state
        Then: Should include both in message
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        state = self.fake.random_element(["pending", "approved", "rejected"])
        exc = DocumentNotEditableException(doc_id, state)
        self.assertIn(str(doc_id), exc.message)
        self.assertIn(state, exc.message)

    def test_document_not_editable_success_attributes(self) -> None:
        """
        When: Created with document_id and current_state
        Then: Should store both as attributes
        """
        doc_id = self.fake.random_int(min=1, max=99_999)
        state = self.fake.random_element(["pending", "approved", "rejected"])
        exc = DocumentNotEditableException(doc_id, state)
        self.assertEqual(exc.document_id, doc_id)
        self.assertEqual(exc.current_state, state)

    def test_document_not_editable_success_draft_mention(self) -> None:
        """
        When: Created
        Then: Message should mention DRAFT state requirement
        """
        exc = DocumentNotEditableException(self.fake.random_int(min=1, max=99_999), "pending")
        self.assertIn("DRAFT", exc.message)

    def test_document_not_editable_success_inherits_domain(self) -> None:
        """
        When: Created
        Then: Should be a DomainException
        """
        exc = DocumentNotEditableException(self.fake.random_int(min=1, max=99_999), "approved")
        self.assertIsInstance(exc, DomainException)
