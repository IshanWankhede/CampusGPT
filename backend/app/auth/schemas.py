import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.otp_verification import OtpPurpose
from app.models.role_request import RoleRequestStatus
from app.models.user import AuthProvider, CollegeName, UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.STUDENT
    college: CollegeName = CollegeName.VIT

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: UserRole) -> UserRole:
        if v == UserRole.ADMIN:
            raise ValueError("Administrator role cannot be requested publicly")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    college: CollegeName = CollegeName.VIT


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class SendOtpRequest(BaseModel):
    email: EmailStr
    purpose: OtpPurpose
    college: CollegeName | None = None


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    purpose: OtpPurpose


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(min_length=8, max_length=128)


class RoleRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None
    applicant_email: str
    requested_role: UserRole
    status: RoleRequestStatus
    reviewed_by: uuid.UUID | None = None
    reviewed_at: datetime | None = None
    note: str | None = None
    created_at: datetime


class RoleRequestReviewAction(BaseModel):
    note: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    college: CollegeName | None = None
    auth_provider: AuthProvider = AuthProvider.LOCAL
    profile_picture: str | None = None
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
    pending_role_request: RoleRequestResponse | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
