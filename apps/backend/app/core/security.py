"""Security primitives: password hashing and JWT encode/decode.

Kept free of FastAPI/DB imports so it is unit-testable in isolation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any, Literal

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TokenType = Literal["access", "refresh"]


class Role(StrEnum):
    """RBAC roles in ascending privilege order semantics handled by ROLE_RANK."""

    VIEWER = "viewer"
    ENGINEER = "engineer"
    ADMIN = "admin"
    OWNER = "owner"


# Higher rank = more privilege. Used by require_role for hierarchical checks.
ROLE_RANK: dict[str, int] = {
    Role.VIEWER: 0,
    Role.ENGINEER: 1,
    Role.ADMIN: 2,
    Role.OWNER: 3,
}


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return _pwd_context.verify(plain, hashed)


def _create_token(
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(
    subject: str, extra_claims: dict[str, Any] | None = None
) -> str:
    """Create a short-lived access token."""
    settings = get_settings()
    return _create_token(
        subject,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims,
    )


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token."""
    settings = get_settings()
    return _create_token(
        subject,
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any]:
    """Decode and validate a JWT, optionally asserting its `type` claim.

    Raises jwt exceptions on invalid/expired tokens; callers map these to 401.
    """
    settings = get_settings()
    payload: dict[str, Any] = jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
    if expected_type is not None and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"Expected token type {expected_type!r}")
    return payload
