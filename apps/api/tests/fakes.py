"""Implementaciones en memoria de los puertos, para las pruebas unitarias."""

import dataclasses
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime

from entrevecinos.application.users.ports import AccessToken
from entrevecinos.domain.communities.entities import (
    Community,
    Membership,
    MembershipRole,
    MembershipStatus,
    NewCommunity,
)
from entrevecinos.domain.users.entities import NewUser, PlatformRole, User
from entrevecinos.domain.users.errors import EmailAlreadyRegistered, NotAuthenticated


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[uuid.UUID, User] = {}
        self.password_hashes: dict[uuid.UUID, str] = {}

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)

    def get_credentials(self, email: str) -> tuple[User, str] | None:
        user = self.get_by_email(email)
        return (user, self.password_hashes[user.id]) if user else None

    def update_password_hash(self, user_id: uuid.UUID, password_hash: str) -> None:
        self.password_hashes[user_id] = password_hash

    def update_profile(self, user_id: uuid.UUID, values: Mapping[str, str | None]) -> User:
        self.users[user_id] = dataclasses.replace(self.users[user_id], **values)
        return self.users[user_id]

    def add(self, user: NewUser, password_hash: str) -> User:
        if self.get_by_email(user.email):
            raise EmailAlreadyRegistered(user.email)
        stored = User(
            id=uuid.uuid4(),
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            platform_role=PlatformRole.USER,
            is_active=True,
            created_at=datetime.now(UTC),
        )
        self.users[stored.id] = stored
        self.password_hashes[stored.id] = password_hash
        return stored


class FakePasswordHasher:
    """`hashed:<contraseña>`; los hashes `old:<contraseña>` se consideran desactualizados."""

    def __init__(self) -> None:
        self.verified: list[str | None] = []

    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify_and_update(
        self, password: str, password_hash: str | None
    ) -> tuple[bool, str | None]:
        self.verified.append(password_hash)
        if password_hash == f"old:{password}":
            return True, self.hash(password)
        return password_hash == self.hash(password), None


class FakeTokenIssuer:
    def issue(self, user_id: uuid.UUID) -> AccessToken:
        return AccessToken(token=f"token-for:{user_id}", expires_in=3600)

    def decode(self, token: str) -> uuid.UUID:
        if not token.startswith("token-for:"):
            raise NotAuthenticated
        return uuid.UUID(token.removeprefix("token-for:"))


class InMemoryCommunityRepository:
    def __init__(self) -> None:
        self.communities: dict[uuid.UUID, Community] = {}
        self.memberships: dict[tuple[uuid.UUID, uuid.UUID], Membership] = {}

    def add(self, community: NewCommunity, admin_id: uuid.UUID) -> Community:
        now = datetime.now(UTC)
        stored = Community(
            id=uuid.uuid4(),
            name=community.name,
            description=community.description,
            postal_code=community.postal_code,
            city=community.city,
            created_by=admin_id,
            is_active=True,
            created_at=now,
        )
        self.communities[stored.id] = stored
        self.memberships[(stored.id, admin_id)] = Membership(
            community_id=stored.id,
            user_id=admin_id,
            role=MembershipRole.COMMUNITY_ADMIN,
            status=MembershipStatus.APPROVED,
            requested_at=now,
            reviewed_by=admin_id,
            reviewed_at=now,
            joined_at=now,
        )
        return stored

    def get(self, community_id: uuid.UUID) -> Community | None:
        community = self.communities.get(community_id)
        return community if community and community.is_active else None
