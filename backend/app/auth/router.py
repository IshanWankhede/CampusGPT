import urllib.parse
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
import httpx
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
from app.core.config import settings
from app.core.dependencies import get_current_user, require_role
from app.database.session import get_db
from app.models.user import CollegeName, User, UserRole

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
            if "verify your email" in message or "college email" in message
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        raise HTTPException(status_code=code, detail=message) from exc


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: DbSession) -> TokenResponse:
    try:
        user = service.authenticate_user(db, request.email, request.password, request.college)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

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


@router.get("/google/login")
def google_login(college: str | None = None) -> RedirectResponse:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth?error={urllib.parse.quote('Google OAuth is not configured on the server. Please set GOOGLE_CLIENT_ID in backend/.env.')}"
        )

    if not college:
        raise HTTPException(status_code=400, detail="Please select your college first.")
    try:
        college_enum = CollegeName(college)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid college selected.") from None

    state = service.create_oauth_state(college_enum)
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
def google_callback(
    db: DbSession,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    def redirect_error(msg: str) -> RedirectResponse:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth?error={urllib.parse.quote(msg)}"
        )

    if error or not code or not state:
        return redirect_error("OAuth authentication cancelled or failed.")

    try:
        selected_college = service.verify_oauth_state(state)
    except ValueError as exc:
        return redirect_error(str(exc))

    try:
        with httpx.Client(timeout=10.0) as client:
            token_res = client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            if not token_res.is_success:
                return redirect_error("Failed to exchange Google OAuth authorization code.")
            token_data = token_res.json()
            access_token = token_data.get("access_token")

            userinfo_res = client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if not userinfo_res.is_success:
                return redirect_error("Failed to fetch Google user profile.")
            userinfo = userinfo_res.json()
    except Exception:
        return redirect_error("Unable to connect to Google OAuth service.")

    email = userinfo.get("email", "").strip().lower()
    email_verified = userinfo.get("email_verified", False)
    google_sub = userinfo.get("sub")
    full_name = userinfo.get("name") or (email.split("@")[0] if email else "Campus User")
    profile_picture = userinfo.get("picture")

    if not email or not email_verified:
        return redirect_error("Google email is not verified.")

    try:
        derived_college = service.derive_college_from_email(email)
    except ValueError as exc:
        return redirect_error(str(exc))

    if selected_college != derived_college:
        return redirect_error("The selected college does not match your Google email domain.")

    user = service.repository.get_user_by_email(db, email)
    if user is not None:
        if user.college and user.college != derived_college:
            return redirect_error("The selected college does not match your registered institution.")
        if not user.college:
            user.college = derived_college
        if not user.google_id:
            user.google_id = google_sub
        if not user.profile_picture:
            user.profile_picture = profile_picture
        user.is_email_verified = True
        db.commit()
    else:
        user = service.repository.create_google_user(
            db,
            email=email,
            full_name=full_name,
            college=derived_college,
            google_id=google_sub,
            profile_picture=profile_picture,
        )

    access_token = service.create_access_token(user)
    refresh_token = service.create_refresh_token(user)

    target_url = f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(url=target_url)


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
        service.create_and_send_otp(
            db, user, request.purpose, email=request.email, college=request.college
        )
    except ValueError as exc:
        code = 429 if "Too many" in str(exc) else 400
        raise HTTPException(status_code=code, detail=str(exc)) from exc
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

