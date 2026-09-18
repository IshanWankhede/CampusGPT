from datetime import datetime, timedelta, timezone
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import repository
from app.auth.schemas import RegisterRequest
from app.core.config import settings
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
        return repository.create_user(
            db,
            email=request.email,
            hashed_password=hash_password(request.password),
            full_name=request.full_name,
            role=request.role,
        )
    except IntegrityError:
        db.rollback()
        raise ValueError("A user with this email already exists") from None


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = repository.get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


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
