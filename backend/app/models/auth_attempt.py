from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AuthAttempt(Base):
    """Logs authentication attempts for database-backed rate limiting (WP5).

    Stores only SHA-256 hashes of identifiers (emails, usernames) and IP
    addresses so this table does not become a second store of personal data.
    """

    __tablename__ = "auth_attempts"
    __table_args__ = (
        Index("ix_auth_attempts_action_ident_created", "action", "identifier_hash", "created_at"),
        Index("ix_auth_attempts_action_ip_created", "action", "ip_hash", "created_at"),
        Index("ix_auth_attempts_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    identifier_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ip_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

