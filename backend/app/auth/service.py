from datetime import datetime, timedelta, timezone
import secrets
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import repository
from app.auth.schemas import RegisterRequest
from app.core.config import settings
from app.core.email import reset_email, send_email, verification_email
from app.models.otp_verification import OtpPurpose
from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def register_user(db: Session, request: RegisterRequest) -> User:
    if repository.get_user_by_email(db, request.email):
        raise ValueError("A user with this email already exists")
    try:
        user = repository.create_user(
            db,
            email=request.email,
            hashed_password=hash_password(request.password),
            full_name=request.full_name,
            role=request.role,
        )
        create_and_send_otp(db, user, OtpPurpose.EMAIL_VERIFY)
        return user
    except IntegrityError:
        db.rollback()
        raise ValueError("A user with this email already exists") from None


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = repository.get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_and_send_otp(db: Session, user: User, purpose: OtpPurpose) -> None:
    if repository.count_recent_otps(db, user.id, purpose) >= 3:
        raise ValueError("Too many requests, please wait before requesting another code")
    otp = generate_otp()
    repository.create_otp(
        db,
        user_id=user.id,
        otp_hash=hash_password(otp),
        purpose=purpose,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    if purpose == OtpPurpose.EMAIL_VERIFY:
        send_email(user.email, "Verify your CampusGPT email", verification_email(otp))
    else:
        send_email(user.email, "Reset your CampusGPT password", reset_email(otp))


def verify_otp(db: Session, user: User, otp: str, purpose: OtpPurpose) -> bool:
    record = repository.get_latest_active_otp(db, user.id, purpose)
    now = datetime.now(timezone.utc)
    if record is None or record.expires_at <= now:
        raise ValueError("Invalid or expired code")
    if record.attempts >= 5:
        record.is_used = True
        db.commit()
        raise ValueError("Too many failed attempts, please request a new code")
    if not verify_password(otp, record.otp_hash):
        record.attempts += 1
        if record.attempts >= 5:
            record.is_used = True
        db.commit()
        if record.attempts >= 5:
            raise ValueError("Too many failed attempts, please request a new code")
        raise ValueError("Incorrect code")
    record.is_used = True
    db.commit()
    return True


def create_token(user: User, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "role": user.role.value,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user: User) -> str:
    return create_token(
        user, "access", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(user: User) -> str:
    return create_token(user, "refresh", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))


def decode_token(token: str, expected_type: str) -> dict:
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise JWTError("Invalid token type or subject")
    return payload


def parse_user_id(payload: dict) -> uuid.UUID:
    try:
        return uuid.UUID(str(payload["sub"]))
    except (KeyError, ValueError, TypeError) as exc:
        raise JWTError("Invalid subject") from exc


def role_from_claim(payload: dict) -> UserRole:
    try:
        return UserRole(payload["role"])
    except (KeyError, ValueError, TypeError) as exc:
        raise JWTError("Invalid role claim") from exc
