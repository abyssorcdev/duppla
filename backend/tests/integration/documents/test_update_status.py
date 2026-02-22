"""Integration tests for UpdateStatus service (PATCH)."""

import pytest

from app.application.dtos.document_dtos import UpdateStatusRequest
from app.application.services.update_status import UpdateStatus
from app.domain.entities.document.status import DocumentStatus
from app.domain.exceptions import InvalidStateTransitionException
from app.infrastructure.database.models import AuditLogModel, DocumentModel

from .conftest import create_draft, fake


class TestUpdateStatusApprovalFlow:
    """Verify the full approval flow persists correctly."""

    def test_full_approval_flow(self, db):
        """
        When: Document goes through DRAFT -> PENDING -> APPROVED
        Then: Each status persists in the database
        """
        user_email = fake.email()
        approver_email = fake.email()

        result = create_draft(db)
        assert result.status == "draft"

        row = db.query(DocumentModel).filter_by(id=result.id).first()
        assert row is not None
        assert row.status == "draft"

        status_svc = UpdateStatus(db=db)

        pending = status_svc.execute(
            result.id,
            UpdateStatusRequest(new_status=DocumentStatus.PENDING),
            user_email,
        )
        assert pending.status == "pending"

        db.expire_all()
        row = db.query(DocumentModel).filter_by(id=result.id).first()
        assert row.status == "pending"

        approved = status_svc.execute(
            result.id,
            UpdateStatusRequest(new_status=DocumentStatus.APPROVED),
            approver_email,
        )
        assert approved.status == "approved"

        db.expire_all()
        row = db.query(DocumentModel).filter_by(id=result.id).first()
        assert row.status == "approved"


class TestUpdateStatusRejection:
    """Verify rejection flow with comment metadata."""

    def test_rejection_stores_comment_in_metadata(self, db):
        """
        When: Document is rejected with a comment
        Then: Rejection comment and reviewer email are stored in metadata
        """
        user_email = fake.email()
        reviewer_email = fake.email()
        rejection_comment = fake.sentence()

        result = create_draft(db)
        status_svc = UpdateStatus(db=db)

        status_svc.execute(
            result.id,
            UpdateStatusRequest(new_status=DocumentStatus.PENDING),
            user_email,
        )

        rejected = status_svc.execute(
            result.id,
            UpdateStatusRequest(
                new_status=DocumentStatus.REJECTED,
                comment=rejection_comment,
            ),
            reviewer_email,
        )
        assert rejected.status == "rejected"

        db.expire_all()
        row = db.query(DocumentModel).filter_by(id=result.id).first()
        assert row.status == "rejected"
        assert row.extra_data["rejection_comment"] == rejection_comment
        assert row.extra_data["rejected_by"] == reviewer_email


class TestUpdateStatusInvalidTransitions:
    """Verify the state machine rejects invalid transitions."""

    def test_draft_to_approved_blocked(self, db):
        """
        When: Trying to skip PENDING and go directly DRAFT -> APPROVED
        Then: Should raise InvalidStateTransitionException
        """
        user_email = fake.email()
        result = create_draft(db)

        with pytest.raises(InvalidStateTransitionException):
            UpdateStatus(db=db).execute(
                result.id,
                UpdateStatusRequest(new_status=DocumentStatus.APPROVED),
                user_email,
            )

    def test_approved_is_final(self, db):
        """
        When: Document is APPROVED (final state)
        Then: Any further transition should raise InvalidStateTransitionException
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

        for target in [DocumentStatus.PENDING, DocumentStatus.REJECTED]:
            with pytest.raises(InvalidStateTransitionException):
                status_svc.execute(
                    result.id,
                    UpdateStatusRequest(new_status=target),
                    user_email,
                )


class TestUpdateStatusAudit:
    """Verify status changes generate audit trail."""

    def test_status_change_generates_audit(self, db):
        """
        When: Document status changes
        Then: An audit_logs entry with action='state_change' should exist
        """
        user_email = fake.email()
        result = create_draft(db)
        UpdateStatus(db=db).execute(
            result.id,
            UpdateStatusRequest(new_status=DocumentStatus.PENDING),
            user_email,
        )

        db.expire_all()
        audit = (
            db.query(AuditLogModel)
            .filter_by(
                table_name="documents",
                record_id=str(result.id),
                action="state_change",
            )
            .first()
        )
        assert audit is not None
        assert audit.old_value == "draft"
        assert audit.new_value == "pending"
