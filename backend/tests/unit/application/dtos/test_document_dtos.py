"""Tests for app.application.dtos.document_dtos – validation edge cases."""

from decimal import Decimal

from pydantic import ValidationError

from tests.common import BaseTestCase

from app.application.dtos.document_dtos import (
    CreateDocumentRequest,
    MAX_AMOUNT,
    MAX_METADATA_KEYS,
    UpdateDocumentRequest,
    UpdateStatusRequest,
)
from app.domain.entities.document.status import DocumentStatus


class TestCreateDocumentRequestAmountExceedsMax(BaseTestCase):
    """Tests for CreateDocumentRequest.validate_amount exceeding MAX_AMOUNT."""

    def test_create_amount_exceeds_max_raises(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            CreateDocumentRequest(
                type="invoice",
                amount=MAX_AMOUNT + Decimal("0.01"),
                metadata={},
            )
        self.assertIn("Amount cannot exceed", str(ctx.exception))


class TestCreateDocumentRequestMetadataExceedsMax(BaseTestCase):
    """Tests for CreateDocumentRequest.validate_metadata exceeding MAX_METADATA_KEYS."""

    def test_create_metadata_too_many_keys_raises(self) -> None:
        big_meta = {f"key_{i}": self.fake.word() for i in range(MAX_METADATA_KEYS + 1)}
        with self.assertRaises(ValidationError) as ctx:
            CreateDocumentRequest(
                type="invoice",
                amount=Decimal("100.00"),
                metadata=big_meta,
            )
        self.assertIn("Metadata cannot have more than", str(ctx.exception))


class TestUpdateDocumentRequestAmountExceedsMax(BaseTestCase):
    """Tests for UpdateDocumentRequest.validate_amount exceeding MAX_AMOUNT."""

    def test_update_amount_exceeds_max_raises(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            UpdateDocumentRequest(
                amount=MAX_AMOUNT + Decimal("0.01"),
                user_id=self.fake.bothify("user-####"),
            )
        self.assertIn("Amount cannot exceed", str(ctx.exception))


class TestUpdateDocumentRequestMetadataExceedsMax(BaseTestCase):
    """Tests for UpdateDocumentRequest.validate_metadata exceeding MAX_METADATA_KEYS."""

    def test_update_metadata_too_many_keys_raises(self) -> None:
        big_meta = {f"key_{i}": self.fake.word() for i in range(MAX_METADATA_KEYS + 1)}
        with self.assertRaises(ValidationError) as ctx:
            UpdateDocumentRequest(
                metadata=big_meta,
                user_id=self.fake.bothify("user-####"),
            )
        self.assertIn("Metadata cannot have more than", str(ctx.exception))


class TestUpdateStatusRequestDraftBlocked(BaseTestCase):
    """Tests for UpdateStatusRequest.validate_new_status blocking DRAFT."""

    def test_update_status_draft_target_raises(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            UpdateStatusRequest(new_status=DocumentStatus.DRAFT)
        self.assertIn("Cannot transition to DRAFT", str(ctx.exception))

    def test_update_status_valid_targets_accepted(self) -> None:
        for target in [DocumentStatus.PENDING, DocumentStatus.APPROVED, DocumentStatus.REJECTED]:
            req = UpdateStatusRequest(new_status=target)
            self.assertEqual(req.new_status, target)
