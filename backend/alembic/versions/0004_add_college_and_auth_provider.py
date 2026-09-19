"""Add college and auth provider to users table."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    college_enum = postgresql.ENUM("COEP", "PICT", "VIT", name="college_name", create_type=False)
    college_enum.create(op.get_bind(), checkfirst=True)

    auth_provider_enum = postgresql.ENUM("LOCAL", "GOOGLE", name="auth_provider", create_type=False)
    auth_provider_enum.create(op.get_bind(), checkfirst=True)

    op.add_column("users", sa.Column("college", college_enum, nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "auth_provider",
            auth_provider_enum,
            nullable=False,
            server_default="LOCAL",
        ),
    )
    op.add_column("users", sa.Column("google_id", sa.String(length=255), nullable=True))
    op.create_unique_constraint("uq_users_google_id", "users", ["google_id"])
    op.add_column("users", sa.Column("profile_picture", sa.String(length=1024), nullable=True))
    op.alter_column("users", "hashed_password", nullable=True)


def downgrade() -> None:
    op.alter_column("users", "hashed_password", nullable=False)
    op.drop_column("users", "profile_picture")
    op.drop_constraint("uq_users_google_id", "users", type_="unique")
    op.drop_column("users", "google_id")
    op.drop_column("users", "auth_provider")
    op.drop_column("users", "college")
    op.execute("DROP TYPE IF EXISTS auth_provider")
    op.execute("DROP TYPE IF EXISTS college_name")
