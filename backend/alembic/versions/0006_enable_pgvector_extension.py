"""Enable pgvector extension.

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-09
"""

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    # Deliberate no-op: dropping the vector extension would destroy any future vector data
    pass
