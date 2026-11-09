import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.user import UserRole


class RoleRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RoleRequest(Base):
    """Stores role elevation requests (e.g. STUDENT requesting FACULTY).

    Audit Retention Policy:
    To preserve role request audit history even if a user account is deleted,
    both user_id and reviewed_by use ON DELETE SET NULL, and applicant_email
    is stored directly to maintain an immutable audit trail without breaking
    referential integrity.
    """
    __tablename__ = "role_requests"
    __table_args__ = (
        Index("ix_role_requests_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    applicant_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    requested_role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_type=False), nullable=False
    )
    status: Mapped[RoleRequestStatus] = mapped_column(
        Enum(RoleRequestStatus, name="role_request_status", native_enum=True),
        nullable=False,
        default=RoleRequestStatus.PENDING,
        server_default="PENDING",
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
