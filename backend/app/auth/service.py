from datetime import datetime, timedelta, timezone
import hmac
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
from app.models.role_request import RoleRequestStatus
from app.models.user import CollegeName, User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pre-computed valid bcrypt dummy hash for timing attack mitigation on unknown users / null passwords
DUMMY_BCRYPT_HASH = "$2b$12$UDL8pWbn.eMsGObcChigK.9babTnY27JsavEtMukzl3OJ526.vfUC"

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


def create_oauth_state(college: CollegeName, nonce: str | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "college": college.value,
        "nonce": nonce or secrets.token_urlsafe(32),
        "type": "oauth_state",
        "iat": now,
        "exp": now + timedelta(minutes=10),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_oauth_state(state_token: str, expected_nonce: str | None = None) -> CollegeName:
    try:
        payload = jwt.decode(
            state_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "oauth_state" or not payload.get("college"):
            raise ValueError("Invalid OAuth state type")
        if expected_nonce is not None:
            actual_nonce = str(payload.get("nonce", ""))
            if not hmac.compare_digest(actual_nonce, expected_nonce):
                raise ValueError("OAuth state validation failed: nonce mismatch")
        return CollegeName(payload["college"])
    except Exception as exc:
        raise ValueError("Invalid or expired OAuth state") from exc


def get_oauth_state_nonce(state_token: str) -> str | None:
    try:
        payload = jwt.decode(
            state_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("nonce")
    except Exception:
        return None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def register_user(db: Session, request: RegisterRequest) -> User:
    email = request.email.lower().strip()
    validate_college_email_domain(email, request.college)
    if repository.get_user_by_email(db, email):
        raise ValueError("A user with this email already exists")
    if not repository.has_recent_verified_email_otp(db, email):
        raise ValueError("Please verify your email before creating an account")

    # Public registration strictly restricted: Admin role forbidden
    if request.role == UserRole.ADMIN:
        raise ValueError("Administrator role cannot be requested publicly")

    try:
        # Public registration always creates account with STUDENT role
        user = repository.create_user(
            db,
            email=email,
            hashed_password=hash_password(request.password),
            full_name=request.full_name,
            role=UserRole.STUDENT,
            college=request.college,
        )
        user.is_email_verified = True
        db.commit()

        # If user requested FACULTY, record a PENDING role request
        if request.role == UserRole.FACULTY:
            repository.create_role_request(
                db,
                user_id=user.id,
                applicant_email=user.email,
                requested_role=UserRole.FACULTY,
                note="Public registration faculty role request",
            )

        return user
    except IntegrityError:
        db.rollback()
        raise ValueError("A user with this email already exists") from None


def authenticate_user(
    db: Session, email: str, password: str, college: CollegeName | None = None
) -> User | None:
    user = repository.get_user_by_email(db, email)
    if user is None:
        # Equalize execution timing when user does not exist
        verify_password(password, DUMMY_BCRYPT_HASH)
        return None
    if user.hashed_password is None:
        # Defect C1 fix: Google OAuth or null-hash accounts cannot authenticate via password
        verify_password(password, DUMMY_BCRYPT_HASH)
        return None
    if not verify_password(password, user.hashed_password):
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
    target_email = (email or (user.email if user else "")).lower().strip()
    if not target_email:
        raise ValueError("An email address is required")

    # Mandatory institutional domain verification for EMAIL_VERIFY
    if purpose == OtpPurpose.EMAIL_VERIFY:
        derived_college = derive_college_from_email(target_email)
        if college is not None and derived_college != college:
            raise ValueError("The selected college does not match your email domain.")

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
    target_email = (email or (user.email if user else "")).lower().strip()
    record = repository.get_latest_active_otp(
        db, purpose, user_id=user.id if user else None, email=target_email if target_email else None
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

    # Defect C2 fix: Record verified_at only upon successful OTP verification
    record.is_used = True
    record.verified_at = datetime.now(timezone.utc)
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


def create_refresh_token(
    user: User,
    db: Session | None = None,
    *,
    family_id: uuid.UUID | None = None,
    user_agent: str | None = None,
    ip_hash: str | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    jti = uuid.uuid4()
    fam_id = family_id or uuid.uuid4()

    payload = {
        "sub": str(user.id),
        "jti": str(jti),
        "family_id": str(fam_id),
        "role": user.role.value,
        "type": "refresh",
        "iat": now,
        "exp": expires_at,
    }

    if db is not None:
        repository.create_refresh_token_record(
            db,
            jti=jti,
            family_id=fam_id,
            user_id=user.id,
            issued_at=now,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_hash=ip_hash,
        )

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def rotate_refresh_token(
    db: Session,
    raw_token: str,
    user_agent: str | None = None,
    ip_hash: str | None = None,
) -> tuple[str, str, User]:
    payload = decode_token(raw_token, "refresh")
    raw_jti = payload.get("jti")
    raw_family_id = payload.get("family_id")

    if not raw_jti or not raw_family_id:
        raise ValueError("Invalid or legacy refresh token. Please sign in again.")

    try:
        token_jti = uuid.UUID(str(raw_jti))
        token_family_id = uuid.UUID(str(raw_family_id))
    except (ValueError, TypeError):
        raise ValueError("Invalid refresh token")

    token_record = repository.get_refresh_token_by_jti_for_update(db, token_jti)
    if token_record is None:
        # Unknown/untracked tokens cannot trigger family revocation
        raise ValueError("Invalid refresh token")

    now = datetime.now(timezone.utc)

    # Check reuse
    if token_record.revoked_at is not None:
        elapsed = (now - token_record.revoked_at).total_seconds()
        if elapsed <= settings.REFRESH_TOKEN_LEEWAY_SECONDS:
            # Benign concurrent tab race: reject without revoking family
            raise ValueError("Refresh token already rotated. Please use the newest token.")
        else:
            # Malicious reuse: revoke the entire family
            repository.revoke_refresh_token_family(db, token_record.family_id)
            raise ValueError("Compromised refresh token reuse detected. All sessions in this family have been terminated.")

    if token_record.expires_at <= now:
        token_record.revoked_at = now
        db.commit()
        raise ValueError("Refresh token expired")

    user = repository.get_user_by_id(db, token_record.user_id)
    if user is None or not user.is_active:
        token_record.revoked_at = now
        db.commit()
        raise ValueError("User account deactivated")

    # Valid token: perform atomic rotation
    new_jti = uuid.uuid4()
    token_record.revoked_at = now
    token_record.replaced_by = new_jti

    new_expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    repository.create_refresh_token_record(
        db,
        jti=new_jti,
        family_id=token_record.family_id,
        user_id=user.id,
        issued_at=now,
        expires_at=new_expires_at,
        user_agent=user_agent,
        ip_hash=ip_hash,
    )

    new_access_token = create_access_token(user)
    new_payload = {
        "sub": str(user.id),
        "jti": str(new_jti),
        "family_id": str(token_record.family_id),
        "role": user.role.value,
        "type": "refresh",
        "iat": now,
        "exp": new_expires_at,
    }
    new_refresh_token = jwt.encode(new_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    db.commit()

    return new_access_token, new_refresh_token, user


def revoke_token_family_by_token(db: Session, raw_token: str) -> None:
    try:
        payload = decode_token(raw_token, "refresh")
        raw_jti = payload.get("jti")
        if raw_jti:
            token_jti = uuid.UUID(str(raw_jti))
            token = repository.get_refresh_token_by_jti(db, token_jti)
            if token:
                repository.revoke_refresh_token_family(db, token.family_id)
    except Exception:
        pass


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
