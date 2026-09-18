"""Allow email OTPs before registration."""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002_add_email_verification"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("otp_verifications", sa.Column("email", sa.String(length=255), nullable=True))
    op.alter_column("otp_verifications", "user_id", nullable=True)
    op.create_index("ix_otp_email_purpose_used", "otp_verifications", ["email", "purpose", "is_used"])


def downgrade() -> None:
    op.drop_index("ix_otp_email_purpose_used", table_name="otp_verifications")
    op.drop_column("otp_verifications", "email")
    op.alter_column("otp_verifications", "user_id", nullable=False)
