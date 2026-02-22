"""add users table with audit trigger

Revision ID: 0003_users
Revises: 0002_audit_triggers
Create Date: 2026-02-16 00:00:00.000000

Creates the finance.users table and attaches an audit trigger so that
direct database modifications to status/role are recorded in audit_logs.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_users"
down_revision: Union[str, None] = "0002_audit_triggers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("google_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("picture", sa.String(length=512), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("google_id", name="uq_users_google_id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        schema="finance",
    )

    # Trigger function for finance.users — runs AFTER the table exists
    op.execute("""
        CREATE OR REPLACE FUNCTION finance.audit_users_changes()
        RETURNS TRIGGER AS $$
        BEGIN
            IF current_setting('app.skip_audit', true) = 'application' THEN
                RETURN NEW;
            END IF;

            IF OLD.status IS DISTINCT FROM NEW.status THEN
                INSERT INTO finance.audit_logs (table_name, record_id, action, old_value, new_value, user_id)
                VALUES ('users', NEW.id::text, 'state_change',
                        OLD.status, NEW.status, current_user);
            END IF;

            IF OLD.role IS DISTINCT FROM NEW.role THEN
                INSERT INTO finance.audit_logs (table_name, record_id, action, old_value, new_value, user_id)
                VALUES ('users', NEW.id::text, 'field_updated',
                        'role: ' || COALESCE(OLD.role, 'null'),
                        'role: ' || COALESCE(NEW.role, 'null'),
                        current_user);
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_audit_users
        AFTER UPDATE ON finance.users
        FOR EACH ROW EXECUTE FUNCTION finance.audit_users_changes();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_users ON finance.users")
    op.execute("DROP FUNCTION IF EXISTS finance.audit_users_changes()")
    op.drop_table("users", schema="finance")
