"""seed admin user for testing

Revision ID: 0004_seed_admin
Revises: 0003_users
Create Date: 2026-02-21 12:00:00.000000

Inserts a default admin user so the deployed app has at least one
active user who can manage others.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0004_seed_admin"
down_revision: Union[str, None] = "0003_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO finance.users (id, google_id, email, name, role, status)
        VALUES (
            gen_random_uuid(),
            'seed-admin-001',
            'admin@duppla.test',
            'Admin de Prueba',
            'admin',
            'active'
        )
        ON CONFLICT (email) DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("DELETE FROM finance.users WHERE email = 'admin@duppla.test';")
