from datetime import datetime, timedelta, timezone
import hashlib
import logging
import secrets
import urllib.parse
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
import httpx
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.schemas import (
    AccessTokenResponse,
    ForgotPasswordRequest,
    GoogleExchangeRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    RoleRequestResponse,
    SendOtpRequest,
    TokenResponse,
    UserResponse,
    VerifyOtpRequest,
)
from app.core.config import settings
from app.core.dependencies import get_current_user, require_role
from app.database.session import get_db
from app.models.otp_verification import OtpPurpose
from app.models.user import CollegeName, User, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: DbSession) -> UserResponse:
    try:
        user = service.register_user(db, request)
        user_resp = UserResponse.model_validate(user)
        pending_req = service.repository.get_pending_role_request_for_user(db, user.id)
        if pending_req:
            user_resp.pending_role_request = RoleRequestResponse.model_validate(pending_req)
        return user_resp
    except ValueError as exc:
        message = str(exc)
        code = (
            status.HTTP_409_CONFLICT
            if "exists" in message
            else status.HTTP_422_UNPROCESSABLE_ENTITY
            if "Administrator" in message
            else status.HTTP_400_BAD_REQUEST
            if "verify your email" in message or "college email" in message or "domain is not associated" in message
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

    user_resp = UserResponse.model_validate(user)
    pending_req = service.repository.get_pending_role_request_for_user(db, user.id)
    if pending_req:
        user_resp.pending_role_request = RoleRequestResponse.model_validate(pending_req)

    return TokenResponse(
        access_token=service.create_access_token(user),
        refresh_token=service.create_refresh_token(user),
        user=user_resp,
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

    raw_nonce = secrets.token_urlsafe(32)
    state = service.create_oauth_state(college_enum, nonce=raw_nonce)
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    response = RedirectResponse(url=google_auth_url)
    response.set_cookie(
        key="oauth_binding_nonce",
        value=raw_nonce,
        httponly=True,
        samesite="lax",
        secure=(settings.ENV != "development"),
        path="/api/v1/auth",
        max_age=600,
    )
    return response


@router.get("/google/callback")
def google_callback(
    request: Request,
    db: DbSession,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    def redirect_error(msg: str, clear_cookie: bool = False) -> RedirectResponse:
        res = RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth?error={urllib.parse.quote(msg)}"
        )
        res.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        res.headers["Pragma"] = "no-cache"
        res.headers["Referrer-Policy"] = "no-referrer"
        if clear_cookie:
            res.delete_cookie(key="oauth_binding_nonce", path="/api/v1/auth")
        return res

    if error or not code or not state:
        # Untrusted/malformed callback: do NOT clear cookie
        return redirect_error("OAuth authentication cancelled or failed.", clear_cookie=False)

    cookie_nonce = request.cookies.get("oauth_binding_nonce")
    if not cookie_nonce:
        return redirect_error("OAuth state validation failed.", clear_cookie=False)

    try:
        selected_college = service.verify_oauth_state(state, expected_nonce=cookie_nonce)
    except ValueError:
        # Untrusted/tampered state: do NOT clear cookie
        return redirect_error("OAuth state validation failed.", clear_cookie=False)

    # State signature and nonce matched the cookie!
    # Subsequent terminal failures are genuine failures of this flow.
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
                return redirect_error("Failed to exchange Google OAuth authorization code.", clear_cookie=True)
            token_data = token_res.json()
            access_token = token_data.get("access_token")

            userinfo_res = client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if not userinfo_res.is_success:
                return redirect_error("Failed to fetch Google user profile.", clear_cookie=True)
            userinfo = userinfo_res.json()
    except Exception:
        return redirect_error("Unable to connect to Google OAuth service.", clear_cookie=True)

    email = userinfo.get("email", "").strip().lower()
    email_verified = userinfo.get("email_verified", False)
    google_sub = userinfo.get("sub")
    full_name = userinfo.get("name") or (email.split("@")[0] if email else "Campus User")
    profile_picture = userinfo.get("picture")

    if not email or not email_verified:
        return redirect_error("Google email is not verified.", clear_cookie=True)

    try:
        derived_college = service.derive_college_from_email(email)
    except ValueError as exc:
        return redirect_error(str(exc), clear_cookie=True)

    if selected_college != derived_college:
        return redirect_error("The selected college does not match your Google email domain.", clear_cookie=True)

    user = service.repository.get_user_by_email(db, email)
    if user is not None:
        if not user.is_email_verified:
            return redirect_error("Cannot link Google account to an unverified local account.", clear_cookie=True)

        if user.college and user.college != derived_college:
            return redirect_error("The selected college does not match your registered institution.", clear_cookie=True)
        if not user.college:
            user.college = derived_college

        if not user.google_id:
            logger.info("Linking Google account %s to verified user %s", google_sub, user.email)
            user.google_id = google_sub
        elif user.google_id != google_sub:
            return redirect_error("Google identity mismatch for this account.", clear_cookie=True)

        if not user.profile_picture and profile_picture:
            user.profile_picture = profile_picture
        db.commit()
    else:
        user = service.repository.create_google_user(
            db,
            email=email,
            full_name=full_name,
            college=derived_college,
            google_id=google_sub,
            profile_picture=profile_picture,
            role=UserRole.STUDENT,
        )

    # Generate single-use opaque authorization code
    raw_code = secrets.token_urlsafe(32)
    code_hash = hashlib.sha256(raw_code.encode("utf-8")).hexdigest()
    nonce_hash = hashlib.sha256(cookie_nonce.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=60)

    service.repository.create_login_code(
        db,
        user_id=user.id,
        code_hash=code_hash,
        nonce_hash=nonce_hash,
        expires_at=expires_at,
    )

    # Redirect with code only; retain oauth_binding_nonce cookie for exchange
    target_url = f"{settings.FRONTEND_URL}/auth/callback?code={raw_code}"
    res = RedirectResponse(url=target_url)
    res.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    res.headers["Pragma"] = "no-cache"
    res.headers["Referrer-Policy"] = "no-referrer"
    return res


@router.post("/google/exchange", response_model=TokenResponse)
def google_exchange(
    request: Request,
    body: GoogleExchangeRequest,
    response: Response,
    db: DbSession,
) -> TokenResponse:
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"

    # 1. Validate Origin header against configured trusted frontend origins
    trusted_origins = {orig.strip() for orig in settings.CORS_ORIGINS.split(",") if orig.strip()}
    if settings.FRONTEND_URL:
        trusted_origins.add(settings.FRONTEND_URL.strip())

    origin = request.headers.get("origin")
    if not origin or origin not in trusted_origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: untrusted or missing request origin",
        )

    # 2. Validate Content-Type
    content_type = request.headers.get("content-type", "")
    if not content_type.startswith("application/json"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported Media Type: application/json required",
        )

    # 3. Read cookie nonce
    cookie_nonce = request.cookies.get("oauth_binding_nonce")
    if not cookie_nonce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired authorization code",
        )

    # 4. Compute hashes
    code_hash = hashlib.sha256(body.code.encode("utf-8")).hexdigest()
    nonce_hash = hashlib.sha256(cookie_nonce.encode("utf-8")).hexdigest()

    # 5. Atomic PostgreSQL consumption
    user = service.repository.consume_login_code(
        db,
        code_hash=code_hash,
        nonce_hash=nonce_hash,
    )
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired authorization code",
        )

    # 6. Clear cookie on success
    response.delete_cookie(key="oauth_binding_nonce", path="/api/v1/auth")

    # 7. Issue tokens
    user_resp = UserResponse.model_validate(user)
    pending_req = service.repository.get_pending_role_request_for_user(db, user.id)
    if pending_req:
        user_resp.pending_role_request = RoleRequestResponse.model_validate(pending_req)

    return TokenResponse(
        access_token=service.create_access_token(user),
        refresh_token=service.create_refresh_token(user),
        user=user_resp,
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
def me(current_user: Annotated[User, Depends(get_current_user)], db: DbSession) -> UserResponse:
    user_resp = UserResponse.model_validate(current_user)
    pending_req = service.repository.get_pending_role_request_for_user(db, current_user.id)
    if pending_req:
        user_resp.pending_role_request = RoleRequestResponse.model_validate(pending_req)
    return user_resp


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
            except RuntimeError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Email service is temporarily unavailable. Please try again later.",
                ) from exc
        return {"message": "If an account with this email exists, a code has been sent."}

    # EMAIL_VERIFY: enforce mandatory server-side institutional email domain check
    try:
        service.derive_college_from_email(request.email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # User enumeration defense: if account already exists and is verified, return generic success without sending code
    if user is not None and user.is_email_verified:
        return {"message": "Verification code sent"}

    try:
        service.create_and_send_otp(
            db, user, request.purpose, email=request.email, college=request.college
        )
    except ValueError as exc:
        code = 429 if "Too many" in str(exc) else 400
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email service is temporarily unavailable. Please try again later.",
        ) from exc
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

