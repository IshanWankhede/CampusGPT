"""Alter profile_picture to Text.

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-19
"""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "profile_picture",
        existing_type=sa.String(length=1024),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "profile_picture",
        existing_type=sa.Text(),
        type_=sa.String(length=1024),
        existing_nullable=True,
    )
