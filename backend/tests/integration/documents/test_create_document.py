"""Integration tests for CreateDocument service (POST)."""

from app.infrastructure.database.models import AuditLogModel, DocumentModel

from .conftest import create_draft, fake


class TestCreateDocument:
    """Verify document creation persists in the database."""

    def test_create_persists_in_db(self, db):
        """
        When: A document is created with valid data
        Then: It should persist in the database with status 'draft'
        """
        result = create_draft(db)

        assert result.id is not None
        assert result.status == "draft"

        row = db.query(DocumentModel).filter_by(id=result.id).first()
        assert row is not None
        assert row.status == "draft"

    def test_create_with_metadata(self, db):
        """
        When: A document is created with metadata
        Then: Metadata should persist correctly in the database
        """
        client = fake.company()
        project = fake.word()
        metadata = {"client": client, "project": project}
        result = create_draft(db, metadata=metadata)

        db.expire_all()
        row = db.query(DocumentModel).filter_by(id=result.id).first()
        assert row.extra_data["client"] == client
        assert row.extra_data["project"] == project

    def test_create_with_different_types(self, db):
        """
        When: Documents are created with different types
        Then: Each type should persist correctly
        """
        for doc_type in ("invoice", "receipt", "voucher"):
            result = create_draft(db, type=doc_type)
            row = db.query(DocumentModel).filter_by(id=result.id).first()
            assert row.type == doc_type

    def test_create_generates_audit_log(self, db):
        """
        When: A document is created
        Then: An audit_logs entry with action='created' should exist
        """
        result = create_draft(db)

        db.expire_all()
        audit = (
            db.query(AuditLogModel)
            .filter_by(table_name="documents", record_id=str(result.id), action="created")
            .first()
        )
        assert audit is not None
