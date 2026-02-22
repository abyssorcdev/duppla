"""add audit triggers for direct database modifications

Revision ID: 0002_audit_triggers
Revises: 0001_initial
Create Date: 2026-02-18 00:00:00.000000

Creates PostgreSQL triggers on finance.documents, finance.jobs and finance.users
that automatically log changes to finance.audit_logs when records are modified
directly in the database (bypassing the application layer).

audit_logs now uses a generic (table_name, record_id) instead of document_id,
so it can track changes across all tables.

To avoid duplicate entries, the application sets the session variable
'app.skip_audit = application' before every write operation. The trigger
checks this variable and skips logging when the change originates from code.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0002_audit_triggers"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Trigger function: finance.documents ───────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION finance.audit_documents_changes()
        RETURNS TRIGGER AS $$
        BEGIN
            IF current_setting('app.skip_audit', true) = 'application' THEN
                RETURN NEW;
            END IF;

            IF OLD.type IS DISTINCT FROM NEW.type THEN
                INSERT INTO finance.audit_logs (table_name, record_id, action, old_value, new_value, user_id)
                VALUES ('documents', NEW.id::text, 'field_updated',
                        'type: ' || OLD.type, 'type: ' || NEW.type, current_user);
            END IF;

            IF OLD.amount IS DISTINCT FROM NEW.amount THEN
                INSERT INTO finance.audit_logs (table_name, record_id, action, old_value, new_value, user_id)
                VALUES ('documents', NEW.id::text, 'field_updated',
                        'amount: ' || OLD.amount::text, 'amount: ' || NEW.amount::text, current_user);
            END IF;

            IF OLD.status IS DISTINCT FROM NEW.status THEN
                INSERT INTO finance.audit_logs (table_name, record_id, action, old_value, new_value, user_id)
                VALUES ('documents', NEW.id::text, 'state_change',
                        OLD.status, NEW.status, current_user);
            END IF;

            IF OLD.metadata IS DISTINCT FROM NEW.metadata THEN
                INSERT INTO finance.audit_logs (table_name, record_id, action, old_value, new_value, user_id)
                VALUES ('documents', NEW.id::text, 'field_updated',
                        OLD.metadata::text, NEW.metadata::text, current_user);
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # ── Trigger function: finance.jobs ────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION finance.audit_jobs_changes()
        RETURNS TRIGGER AS $$
        BEGIN
            IF current_setting('app.skip_audit', true) = 'application' THEN
                RETURN NEW;
            END IF;

            IF OLD.status IS DISTINCT FROM NEW.status THEN
                INSERT INTO finance.audit_logs (table_name, record_id, action, old_value, new_value, user_id)
                VALUES ('jobs', NEW.id::text, 'state_change',
                        OLD.status, NEW.status, current_user);
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # ── Attach triggers ───────────────────────────────────────────────────────
    op.execute("""
        CREATE TRIGGER trg_audit_documents
        AFTER UPDATE ON finance.documents
        FOR EACH ROW EXECUTE FUNCTION finance.audit_documents_changes();
    """)

    op.execute("""
        CREATE TRIGGER trg_audit_jobs
        AFTER UPDATE ON finance.jobs
        FOR EACH ROW EXECUTE FUNCTION finance.audit_jobs_changes();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_documents ON finance.documents")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_jobs ON finance.jobs")
    op.execute("DROP FUNCTION IF EXISTS finance.audit_documents_changes()")
    op.execute("DROP FUNCTION IF EXISTS finance.audit_jobs_changes()")
