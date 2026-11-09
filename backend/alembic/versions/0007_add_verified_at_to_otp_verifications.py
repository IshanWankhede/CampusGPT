"""Add verified_at to otp_verifications.

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-09
"""

from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "otp_verifications",
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("otp_verifications", "verified_at")

