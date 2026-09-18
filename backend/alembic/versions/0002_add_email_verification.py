"""Add email verification and OTP records."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_add_email_verification"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    purpose = postgresql.ENUM(
        "EMAIL_VERIFY", "PASSWORD_RESET", name="otp_purpose", create_type=False
    )
    purpose.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "otp_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("otp_hash", sa.String(length=255), nullable=False),
        sa.Column("purpose", purpose, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_otp_user_purpose_used", "otp_verifications", ["user_id", "purpose", "is_used"]
    )


def downgrade() -> None:
    op.drop_index("ix_otp_user_purpose_used", table_name="otp_verifications")
    op.drop_table("otp_verifications")
    op.execute("DROP TYPE IF EXISTS otp_purpose")
    op.drop_column("users", "is_email_verified")
