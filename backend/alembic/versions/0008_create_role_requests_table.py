"""Create role_requests table.

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        status_enum = postgresql.ENUM("PENDING", "APPROVED", "REJECTED", name="role_request_status", create_type=False)
        status_enum.create(bind, checkfirst=True)
        user_role_enum = postgresql.ENUM("ADMIN", "FACULTY", "STUDENT", name="user_role", create_type=False)
    else:
        status_enum = sa.Enum("PENDING", "APPROVED", "REJECTED", name="role_request_status")
        user_role_enum = sa.Enum("ADMIN", "FACULTY", "STUDENT", name="user_role")

    op.create_table(
        "role_requests",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("applicant_email", sa.String(length=255), nullable=False),
        sa.Column("requested_role", user_role_enum, nullable=False),
        sa.Column("status", status_enum, nullable=False, server_default="PENDING"),
        sa.Column("reviewed_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_role_requests_user_id", "role_requests", ["user_id"])
    op.create_index("ix_role_requests_applicant_email", "role_requests", ["applicant_email"])
    op.create_index("ix_role_requests_status", "role_requests", ["status"])


def downgrade() -> None:
    op.drop_index("ix_role_requests_status", table_name="role_requests")
    op.drop_index("ix_role_requests_applicant_email", table_name="role_requests")
    op.drop_index("ix_role_requests_user_id", table_name="role_requests")
    op.drop_table("role_requests")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        sa.Enum(name="role_request_status").drop(bind, checkfirst=True)

