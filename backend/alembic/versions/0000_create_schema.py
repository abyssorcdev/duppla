"""create finance schema

Revision ID: 0000_create_schema
Revises:
Create Date: 2026-02-16 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0000_create_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS finance")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS finance CASCADE")
