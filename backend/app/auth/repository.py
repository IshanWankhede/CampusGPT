import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.user import AuthProvider, CollegeName, User, UserRole
from app.models.otp_verification import OtpPurpose, OtpVerification


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


def has_recent_used_email_otp(db: Session, email: str) -> bool:
    return (
        db.scalar(
            select(OtpVerification.id)
            .where(
                OtpVerification.email == email.lower(),
                OtpVerification.purpose == OtpPurpose.EMAIL_VERIFY,
                OtpVerification.is_used.is_(True),
                OtpVerification.expires_at > datetime.now(timezone.utc),
            )
            .limit(1)
        )
        is not None
    )
