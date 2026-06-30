"""Authentication request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserOut


class RegisterRequest(BaseModel):
    """Registration creates a new organization and its owner user."""

    organization_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenPair(BaseModel):
    """Access + refresh token pair returned on login/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthResult(BaseModel):
    """Login/register response: tokens plus the authenticated user."""

    user: UserOut
    tokens: TokenPair


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class PasswordResetIssued(BaseModel):
    """Reset response. `reset_token` is only populated outside production
    (no email transport is configured); in production it is withheld."""

    message: str
    reset_token: str | None = None
