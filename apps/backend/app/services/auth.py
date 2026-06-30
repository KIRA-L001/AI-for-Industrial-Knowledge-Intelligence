"""Authentication business logic: registration, login, refresh, password reset.

Routes stay thin and delegate here; this service owns the rules and persistence
orchestration (Organization + User creation, token issuance).
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.core.config import get_settings
from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import (
    Role,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.organization import Organization
from app.models.user import User
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository
from app.schemas.auth import AuthResult, TokenPair
from app.schemas.user import UserOut


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "org"


class AuthService:
    """Coordinates user/organization repositories and token issuance."""

    def __init__(self, users: UserRepository, orgs: OrganizationRepository) -> None:
        self.users = users
        self.orgs = orgs

    # --- token helpers -------------------------------------------------
    def _issue_tokens(self, user: User) -> TokenPair:
        claims: dict[str, Any] = {"org": str(user.organization_id), "role": user.role}
        return TokenPair(
            access_token=create_access_token(str(user.id), claims),
            refresh_token=create_refresh_token(str(user.id)),
        )

    def _result(self, user: User) -> AuthResult:
        return AuthResult(user=UserOut.model_validate(user), tokens=self._issue_tokens(user))

    async def _unique_slug(self, name: str) -> str:
        base = _slugify(name)
        slug = base
        suffix = 1
        while await self.orgs.get_by_slug(slug) is not None:
            suffix += 1
            slug = f"{base}-{suffix}"
        return slug

    # --- use cases -----------------------------------------------------
    async def register(
        self, *, organization_name: str, email: str, full_name: str, password: str
    ) -> AuthResult:
        """Create a new organization and its owner user."""
        email = email.lower()
        if await self.users.get_by_email(email) is not None:
            raise ConflictError("A user with this email already exists.")

        organization = Organization(
            name=organization_name,
            slug=await self._unique_slug(organization_name),
        )
        organization = await self.orgs.add(organization)

        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=Role.OWNER.value,
            organization_id=organization.id,
        )
        user = await self.users.add(user)
        return self._result(user)

    async def login(self, *, email: str, password: str) -> AuthResult:
        user = await self.users.get_by_email(email.lower())
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled.")
        return self._result(user)

    async def refresh(self, *, refresh_token: str) -> TokenPair:
        from app.core.security import decode_token

        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid or expired refresh token.") from exc

        user = await self.users.get(uuid.UUID(payload["sub"]))
        if user is None or not user.is_active:
            raise UnauthorizedError("User no longer active.")
        return self._issue_tokens(user)

    async def request_password_reset(self, *, email: str) -> str | None:
        """Return a signed reset token if the email exists, else None.

        Callers must not reveal which emails exist (enumeration protection).
        """
        user = await self.users.get_by_email(email.lower())
        if user is None:
            return None
        settings = get_settings()
        now = datetime.now(UTC)
        return jwt.encode(
            {
                "sub": str(user.id),
                "type": "reset",
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(hours=1)).timestamp()),
            },
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    async def confirm_password_reset(self, *, token: str, new_password: str) -> None:
        from app.core.security import decode_token

        try:
            payload = decode_token(token, expected_type="reset")
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid or expired reset token.") from exc

        user = await self.users.get(uuid.UUID(payload["sub"]))
        if user is None:
            raise UnauthorizedError("User not found.")
        user.hashed_password = hash_password(new_password)
        await self.users.add(user)
