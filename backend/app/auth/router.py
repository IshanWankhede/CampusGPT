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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: DbSession) -> TokenResponse:
    user = service.authenticate_user(db, request.email, request.password)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
