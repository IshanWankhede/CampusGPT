from datetime import datetime, timezone
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import repository
from app.auth.schemas import RoleRequestResponse, RoleRequestReviewAction
from app.core.dependencies import require_role
from app.database.session import get_db
from app.models.role_request import RoleRequestStatus
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
DbSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[User, Depends(require_role(UserRole.ADMIN))]


@router.get("/role-requests", response_model=list[RoleRequestResponse])
def list_role_requests(
    _: AdminUser,
    db: DbSession,
    status: RoleRequestStatus | None = None,
) -> list[RoleRequestResponse]:
    """List role requests, optionally filtered by status (PENDING, APPROVED, REJECTED)."""
    requests = repository.get_role_requests(db, status=status)
    return [RoleRequestResponse.model_validate(r) for r in requests]


@router.post(
    "/role-requests/{request_id}/approve",
    response_model=RoleRequestResponse,
)
def approve_role_request(
    request_id: uuid.UUID,
    current_admin: AdminUser,
    db: DbSession,
    action: RoleRequestReviewAction | None = None,
) -> RoleRequestResponse:
    """Approve a pending role request and promote the applicant to requested role."""
    role_req = repository.get_role_request_by_id(db, request_id)
    if not role_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role request not found",
        )

    # Prevent admin self-approval
    if role_req.user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot review or approve their own role requests",
        )

    # Ensure only PENDING requests can be reviewed
    if role_req.status != RoleRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role request is already {role_req.status.value}",
        )

    # Update applicant user role
    if role_req.user_id:
        user = repository.get_user_by_id(db, role_req.user_id)
        if user:
            user.role = role_req.requested_role

    # Update request record
    role_req.status = RoleRequestStatus.APPROVED
    role_req.reviewed_by = current_admin.id
    role_req.reviewed_at = datetime.now(timezone.utc)
    if action and action.note:
        role_req.note = action.note

    db.commit()
    db.refresh(role_req)
    return RoleRequestResponse.model_validate(role_req)


@router.post(
    "/role-requests/{request_id}/reject",
    response_model=RoleRequestResponse,
)
def reject_role_request(
    request_id: uuid.UUID,
    current_admin: AdminUser,
    db: DbSession,
    action: RoleRequestReviewAction | None = None,
) -> RoleRequestResponse:
    """Reject a pending role request. Applicant remains in current role."""
    role_req = repository.get_role_request_by_id(db, request_id)
    if not role_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role request not found",
        )

    # Prevent admin self-review
    if role_req.user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot review or reject their own role requests",
        )

    # Ensure only PENDING requests can be reviewed
    if role_req.status != RoleRequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role request is already {role_req.status.value}",
        )

    # Update request record (user role remains unchanged)
    role_req.status = RoleRequestStatus.REJECTED
    role_req.reviewed_by = current_admin.id
    role_req.reviewed_at = datetime.now(timezone.utc)
    if action and action.note:
        role_req.note = action.note

    db.commit()
    db.refresh(role_req)
    return RoleRequestResponse.model_validate(role_req)

