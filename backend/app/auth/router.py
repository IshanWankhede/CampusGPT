from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.schemas import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    SendOtpRequest,
    VerifyOtpRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.core.dependencies import get_current_user, require_role
from app.database.session import get_db
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: DbSession) -> User:
    try:
        return service.register_user(db, request)
    except ValueError as exc:
        message = str(exc)
        code = (
            status.HTTP_409_CONFLICT
            if "exists" in message
            else status.HTTP_400_BAD_REQUEST
            if "verify your email" in message
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        raise HTTPException(status_code=code, detail=message) from exc


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: DbSession) -> TokenResponse:
    user = service.authenticate_user(db, request.email, request.password)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_email_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email before signing in")
    return TokenResponse(
        access_token=service.create_access_token(user),
        refresh_token=service.create_refresh_token(user),
        user=user,
    )


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(request: RefreshRequest, db: DbSession) -> AccessTokenResponse:
    try:
        payload = service.decode_token(request.refresh_token, "refresh")
        user_id = service.parse_user_id(payload)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from None
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return AccessTokenResponse(access_token=service.create_access_token(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(_: Annotated[User, Depends(get_current_user)]) -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.get(
    "/admin-test",
    response_model=UserResponse,
    summary="Phase 2 RBAC verification endpoint",
)
def admin_test(
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
) -> User:
    return current_user


@router.post("/send-otp")
def send_otp(request: SendOtpRequest, db: DbSession) -> dict[str, str]:
    user = service.repository.get_user_by_email(db, request.email)
    if request.purpose.value == "PASSWORD_RESET":
        if user:
            try:
                service.create_and_send_otp(db, user, request.purpose)
            except ValueError as exc:
                if "Too many" in str(exc):
                    raise HTTPException(status_code=429, detail=str(exc)) from exc
        return {"message": "If an account with this email exists, a code has been sent."}
    if user is not None and user.is_email_verified:
        raise HTTPException(status_code=409, detail="Already verified")
    try:
        service.create_and_send_otp(db, user, request.purpose, email=request.email)
    except ValueError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    return {"message": "Verification code sent"}


@router.post("/verify-otp")
def verify_otp(request: VerifyOtpRequest, db: DbSession) -> dict[str, str]:
    user = service.repository.get_user_by_email(db, request.email)
    try:
        service.verify_otp(db, user, request.otp, request.purpose, email=request.email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if request.purpose.value == "EMAIL_VERIFY" and user is not None:
        user.is_email_verified = True
        db.commit()
    return {"message": "Code verified"}


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: DbSession) -> dict[str, str]:
    return send_otp(SendOtpRequest(email=request.email, purpose="PASSWORD_RESET"), db)


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: DbSession) -> dict[str, str]:
    user = service.repository.get_user_by_email(db, request.email)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    try:
        service.verify_otp(db, user, request.otp, "PASSWORD_RESET")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    user.hashed_password = service.hash_password(request.new_password)
    db.commit()
    return {"message": "Password updated"}
