"""Create login_codes table for secure OAuth code exchange.

Revision ID: 0009
Revises: 0008
Create Date: 2026-11-09
"""

from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "login_codes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("nonce_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("code_hash", name="uq_login_codes_code_hash"),
    )
    op.create_index(
        "ix_login_codes_code_hash",
        "login_codes",
        ["code_hash"],
        unique=False,
    )
    op.create_index(
        "ix_login_codes_user_id",
        "login_codes",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_login_codes_exchange",
        "login_codes",
        ["code_hash", "nonce_hash", "used_at", "expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_login_codes_exchange", table_name="login_codes")
    op.drop_index("ix_login_codes_user_id", table_name="login_codes")
    op.drop_index("ix_login_codes_code_hash", table_name="login_codes")
    op.drop_table("login_codes")
