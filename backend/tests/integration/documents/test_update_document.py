"""Integration tests for UpdateDocument service (PUT)."""

from decimal import Decimal

import pytest

from app.application.dtos.document_dtos import UpdateDocumentRequest, UpdateStatusRequest
from app.application.services.update_document import UpdateDocument
from app.application.services.update_status import UpdateStatus
from app.domain.entities.document.status import DocumentStatus
from app.domain.exceptions import DocumentNotEditableException
from app.infrastructure.database.models import DocumentModel

from .conftest import create_draft, fake


class TestUpdateDocument:
    """Verify UpdateDocument persists changes in the database."""

    def test_update_amount_in_draft(self, db):
        """
        When: Document amount is updated while in DRAFT
        Then: New amount should persist in the database
        """
        initial_amount = Decimal(str(fake.pydecimal(min_value=1, max_value=9999, right_digits=2, positive=True)))
        new_amount = Decimal(str(fake.pydecimal(min_value=10_000, max_value=99_999, right_digits=2, positive=True)))
        user_id = fake.bothify("user-####")

        result = create_draft(db, amount=initial_amount)

        updated = UpdateDocument(db=db).execute(
            result.id,
            UpdateDocumentRequest(amount=new_amount, user_id=user_id),
        )
        assert updated.amount == new_amount

        db.expire_all()
        row = db.query(DocumentModel).filter_by(id=result.id).first()
        assert row.amount == new_amount

    def test_update_then_submit_to_pending(self, db):
        """
        When: Document amount is updated and then submitted
        Then: Updated amount persists and status changes to pending
        """
        initial_amount = Decimal(str(fake.pydecimal(min_value=1, max_value=9999, right_digits=2, positive=True)))
        new_amount = Decimal(str(fake.pydecimal(min_value=10_000, max_value=99_999, right_digits=2, positive=True)))
        user_id = fake.bothify("user-####")
        user_email = fake.email()

        result = create_draft(db, amount=initial_amount)

        UpdateDocument(db=db).execute(
            result.id,
            UpdateDocumentRequest(amount=new_amount, user_id=user_id),
        )

        pending = UpdateStatus(db=db).execute(
            result.id,
            UpdateStatusRequest(new_status=DocumentStatus.PENDING),
            user_email,
        )
        assert pending.status == "pending"

    def test_edit_blocked_in_pending(self, db):
        """
        When: Document is in PENDING state
        Then: Update should raise DocumentNotEditableException
        """
        user_email = fake.email()
        result = create_draft(db)
        UpdateStatus(db=db).execute(
            result.id,
            UpdateStatusRequest(new_status=DocumentStatus.PENDING),
            user_email,
        )

        with pytest.raises(DocumentNotEditableException):
            UpdateDocument(db=db).execute(
                result.id,
                UpdateDocumentRequest(
                    amount=Decimal(str(fake.pydecimal(min_value=1, max_value=9999, right_digits=2, positive=True))),
                    user_id=fake.bothify("user-####"),
                ),
            )

    def test_edit_blocked_in_approved(self, db):
        """
        When: Document is in APPROVED state
        Then: Update should raise DocumentNotEditableException
        """
        user_email = fake.email()
        approver_email = fake.email()

        result = create_draft(db)
        status_svc = UpdateStatus(db=db)
        status_svc.execute(
            result.id,
            UpdateStatusRequest(new_status=DocumentStatus.PENDING),
            user_email,
        )
        status_svc.execute(
            result.id,
            UpdateStatusRequest(new_status=DocumentStatus.APPROVED),
            approver_email,
        )

        with pytest.raises(DocumentNotEditableException):
            UpdateDocument(db=db).execute(
                result.id,
                UpdateDocumentRequest(
                    amount=Decimal(str(fake.pydecimal(min_value=1, max_value=9999, right_digits=2, positive=True))),
                    user_id=fake.bothify("user-####"),
                ),
            )
