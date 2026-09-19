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
from app.models.user import CollegeName, User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

COLLEGE_DOMAIN_MAP: dict[CollegeName, str] = {
    CollegeName.COEP: "coep.ac.in",
    CollegeName.PICT: "pict.edu",
    CollegeName.VIT: "vit.edu",
}

REVERSE_COLLEGE_DOMAIN_MAP: dict[str, CollegeName] = {
    "coep.ac.in": CollegeName.COEP,
    "coep.edu": CollegeName.COEP,
    "coep.edu.in": CollegeName.COEP,
    "pict.edu": CollegeName.PICT,
    "vit.edu": CollegeName.VIT,
}


def validate_college_email_domain(email: str, college: CollegeName) -> None:
    required_domain = COLLEGE_DOMAIN_MAP.get(college)
    actual_domain = email.strip().lower().rsplit("@", 1)[-1]
    if not required_domain or actual_domain != required_domain:
        raise ValueError(f"Please enter a college email containing @{required_domain}")


def derive_college_from_email(email: str) -> CollegeName:
    domain = email.strip().lower().rsplit("@", 1)[-1]
    college = REVERSE_COLLEGE_DOMAIN_MAP.get(domain)
    if not college:
        raise ValueError("This email domain is not associated with a recognized institution.")
    return college


def create_oauth_state(college: CollegeName) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "college": college.value,
        "nonce": secrets.token_hex(16),
        "type": "oauth_state",
        "iat": now,
        "exp": now + timedelta(minutes=10),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_oauth_state(state_token: str) -> CollegeName:
    try:
        payload = jwt.decode(
            state_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "oauth_state" or not payload.get("college"):
            raise ValueError("Invalid OAuth state type")
        return CollegeName(payload["college"])
    except Exception as exc:
        raise ValueError("Invalid or expired OAuth state") from exc


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def register_user(db: Session, request: RegisterRequest) -> User:
    email = request.email.lower()
    validate_college_email_domain(email, request.college)
    if repository.get_user_by_email(db, email):
        raise ValueError("A user with this email already exists")
    if not repository.has_recent_used_email_otp(db, email):
        raise ValueError("Please verify your email before creating an account")
    try:
        user = repository.create_user(
            db,
            email=email,
            hashed_password=hash_password(request.password),
            full_name=request.full_name,
            role=request.role,
            college=request.college,
        )
        user.is_email_verified = True
        db.commit()
        return user
    except IntegrityError:
        db.rollback()
        raise ValueError("A user with this email already exists") from None


def authenticate_user(
    db: Session, email: str, password: str, college: CollegeName | None = None
) -> User | None:
    user = repository.get_user_by_email(db, email)
    if user is None:
        return None
    if user.hashed_password and not verify_password(password, user.hashed_password):
        return None
    if user.role != UserRole.ADMIN:
        if college and user.college and user.college != college:
            raise ValueError("The selected college does not match your registered institution.")
    return user


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_and_send_otp(
    db: Session,
    user: User | None,
    purpose: OtpPurpose,
    *,
    email: str | None = None,
    college: CollegeName | None = None,
) -> None:
    target_email = (email or (user.email if user else "")).lower()
    if not target_email:
        raise ValueError("An email address is required")
    if purpose == OtpPurpose.EMAIL_VERIFY and college is not None:
        validate_college_email_domain(target_email, college)
    if repository.count_recent_otps(
        db, purpose, user_id=user.id if user else None, email=target_email
    ) >= 3:
        raise ValueError("Too many requests, please wait before requesting another code")
    otp = generate_otp()
    repository.create_otp(
        db,
        user_id=user.id if user else None,
        email=target_email,
        otp_hash=hash_password(otp),
        purpose=purpose,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    if purpose == OtpPurpose.EMAIL_VERIFY:
        send_email(target_email, "Verify your CampusGPT email", verification_email(otp))
    else:
        send_email(target_email, "Reset your CampusGPT password", reset_email(otp))


def verify_otp(
    db: Session, user: User | None, otp: str, purpose: OtpPurpose, *, email: str | None = None
) -> bool:
    record = repository.get_latest_active_otp(
        db, purpose, user_id=user.id if user else None, email=(email or user.email).lower() if (email or user) else None
    )
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
