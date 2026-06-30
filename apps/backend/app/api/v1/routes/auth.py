"""Authentication endpoints (register, login, refresh, me, password reset)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import CurrentUser, get_auth_service
from app.core.config import get_settings
from app.schemas.auth import (
    AuthResult,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetIssued,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
)
from app.schemas.user import UserOut
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

AuthDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/register", response_model=AuthResult, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, service: AuthDep) -> AuthResult:
    """Create a new organization and its owner user, returning tokens."""
    return await service.register(
        organization_name=payload.organization_name,
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
    )


@router.post("/login", response_model=AuthResult)
async def login(payload: LoginRequest, service: AuthDep) -> AuthResult:
    return await service.login(email=payload.email, password=payload.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, service: AuthDep) -> TokenPair:
    return await service.refresh(refresh_token=payload.refresh_token)


@router.get("/me", response_model=UserOut)
async def me(current_user: CurrentUser) -> UserOut:
    return UserOut.model_validate(current_user)


@router.post("/password-reset/request", response_model=PasswordResetIssued)
async def request_password_reset(
    payload: PasswordResetRequest, service: AuthDep
) -> PasswordResetIssued:
    """Issue a reset token. Always returns 200 to avoid email enumeration."""
    token = await service.request_password_reset(email=payload.email)
    settings = get_settings()
    return PasswordResetIssued(
        message="If the email exists, a reset link has been sent.",
        reset_token=None if settings.is_production else token,
    )


@router.post(
    "/password-reset/confirm",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def confirm_password_reset(
    payload: PasswordResetConfirm, service: AuthDep
) -> Response:
    await service.confirm_password_reset(
        token=payload.token, new_password=payload.new_password
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
