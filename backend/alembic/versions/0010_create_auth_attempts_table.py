"""Create auth_attempts table for database-backed rate limiting.

Revision ID: 0010
Revises: 0009
Create Date: 2026-11-09
"""

from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_attempts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("identifier_hash", sa.String(length=64), nullable=True),
        sa.Column("ip_hash", sa.String(length=64), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_auth_attempts_action_ident_created",
        "auth_attempts",
        ["action", "identifier_hash", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_auth_attempts_action_ip_created",
        "auth_attempts",
        ["action", "ip_hash", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_auth_attempts_created_at",
        "auth_attempts",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_auth_attempts_created_at", table_name="auth_attempts")
    op.drop_index("ix_auth_attempts_action_ip_created", table_name="auth_attempts")
    op.drop_index("ix_auth_attempts_action_ident_created", table_name="auth_attempts")
    op.drop_table("auth_attempts")

