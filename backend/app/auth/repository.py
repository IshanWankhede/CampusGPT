import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, select, update
from sqlalchemy.orm import Session

from app.models.login_code import LoginCode
from app.models.refresh_token import RefreshToken
from app.models.user import AuthProvider, CollegeName, User, UserRole
from app.models.otp_verification import OtpPurpose, OtpVerification
from app.models.role_request import RoleRequest, RoleRequestStatus


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def create_user(
    db: Session,
    *,
    email: str,
    hashed_password: str,
    full_name: str,
    role: str,
    college: CollegeName | None = None,
) -> User:
    user = User(
        email=email.lower(),
        hashed_password=hashed_password,
        full_name=full_name.strip(),
        role=role,
        college=college,
        auth_provider=AuthProvider.LOCAL,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_google_user(
    db: Session,
    *,
    email: str,
    full_name: str,
    college: CollegeName,
    google_id: str,
    profile_picture: str | None = None,
    role: UserRole = UserRole.STUDENT,
) -> User:
    user = User(
        email=email.lower(),
        hashed_password=None,
        full_name=full_name.strip(),
        role=role,
        college=college,
        auth_provider=AuthProvider.GOOGLE,
        google_id=google_id,
        profile_picture=profile_picture,
        is_email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def count_recent_otps(
    db: Session, purpose: OtpPurpose, *, user_id: uuid.UUID | None = None, email: str | None = None
) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
    return len(
        db.scalars(
            select(OtpVerification).where(
                OtpVerification.purpose == purpose,
                OtpVerification.created_at >= cutoff,
                (OtpVerification.user_id == user_id)
                if user_id is not None
                else (OtpVerification.email == email),
            )
        ).all()
    )


def create_otp(
    db: Session,
    *,
    user_id: uuid.UUID | None,
    email: str,
    otp_hash: str,
    purpose: OtpPurpose,
    expires_at: datetime,
) -> OtpVerification:
    record = OtpVerification(
        user_id=user_id, email=email.lower(), otp_hash=otp_hash, purpose=purpose, expires_at=expires_at
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_latest_active_otp(
    db: Session, purpose: OtpPurpose, *, user_id: uuid.UUID | None = None, email: str | None = None
) -> OtpVerification | None:
    return db.scalar(
        select(OtpVerification)
        .where(
            OtpVerification.purpose == purpose,
            OtpVerification.is_used.is_(False),
            (OtpVerification.user_id == user_id)
            if user_id is not None
            else (OtpVerification.email == email),
        )
        .order_by(desc(OtpVerification.created_at))
        .limit(1)
    )


def has_recent_verified_email_otp(db: Session, email: str) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
    return (
        db.scalar(
            select(OtpVerification.id)
            .where(
                OtpVerification.email == email.lower(),
                OtpVerification.purpose == OtpPurpose.EMAIL_VERIFY,
                OtpVerification.verified_at.is_not(None),
                OtpVerification.verified_at >= cutoff,
            )
            .limit(1)
        )
        is not None
    )


def has_recent_used_email_otp(db: Session, email: str) -> bool:
    # Retained for compatibility; delegates to verified logic
    return has_recent_verified_email_otp(db, email)


def create_role_request(
    db: Session,
    *,
    user_id: uuid.UUID,
    applicant_email: str,
    requested_role: UserRole,
    note: str | None = None,
) -> RoleRequest:
    role_req = RoleRequest(
        user_id=user_id,
        applicant_email=applicant_email.lower(),
        requested_role=requested_role,
        status=RoleRequestStatus.PENDING,
        note=note,
    )
    db.add(role_req)
    db.commit()
    db.refresh(role_req)
    return role_req


def get_role_requests(
    db: Session, status: RoleRequestStatus | None = None
) -> list[RoleRequest]:
    stmt = select(RoleRequest).order_by(desc(RoleRequest.created_at))
    if status is not None:
        stmt = stmt.where(RoleRequest.status == status)
    return list(db.scalars(stmt).all())


def get_role_request_by_id(db: Session, request_id: uuid.UUID) -> RoleRequest | None:
    return db.get(RoleRequest, request_id)


def get_pending_role_request_for_user(
    db: Session, user_id: uuid.UUID
) -> RoleRequest | None:
    return db.scalar(
        select(RoleRequest)
        .where(
            RoleRequest.user_id == user_id,
            RoleRequest.status == RoleRequestStatus.PENDING,
        )
        .order_by(desc(RoleRequest.created_at))
        .limit(1)
    )


def create_login_code(
    db: Session,
    *,
    user_id: uuid.UUID,
    code_hash: str,
    nonce_hash: str,
    expires_at: datetime,
) -> LoginCode:
    record = LoginCode(
        user_id=user_id,
        code_hash=code_hash,
        nonce_hash=nonce_hash,
        expires_at=expires_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def consume_login_code(
    db: Session,
    *,
    code_hash: str,
    nonce_hash: str,
) -> User | None:
    now = datetime.now(timezone.utc)
    stmt = (
        update(LoginCode)
        .where(
            LoginCode.code_hash == code_hash,
            LoginCode.nonce_hash == nonce_hash,
            LoginCode.used_at.is_(None),
            LoginCode.expires_at > now,
        )
        .values(used_at=now)
        .returning(LoginCode.user_id)
    )
    user_id = db.scalar(stmt)
    if user_id is None:
        db.rollback()
        return None
    db.commit()
    return db.get(User, user_id)


def create_refresh_token_record(
    db: Session,
    *,
    jti: uuid.UUID,
    family_id: uuid.UUID,
    user_id: uuid.UUID,
    issued_at: datetime,
    expires_at: datetime,
    user_agent: str | None = None,
    ip_hash: str | None = None,
) -> RefreshToken:
    record = RefreshToken(
        jti=jti,
        family_id=family_id,
        user_id=user_id,
        issued_at=issued_at,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_hash=ip_hash,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_refresh_token_by_jti(db: Session, jti: uuid.UUID) -> RefreshToken | None:
    return db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))


def get_refresh_token_by_jti_for_update(db: Session, jti: uuid.UUID) -> RefreshToken | None:
    return db.scalar(
        select(RefreshToken).where(RefreshToken.jti == jti).with_for_update()
    )


def revoke_refresh_token_family(db: Session, family_id: uuid.UUID) -> int:
    now = datetime.now(timezone.utc)
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    result = db.execute(stmt)
    db.commit()
    return result.rowcount or 0


def revoke_all_user_refresh_tokens(db: Session, user_id: uuid.UUID) -> int:
    now = datetime.now(timezone.utc)
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    result = db.execute(stmt)
    db.commit()
    return result.rowcount or 0



