"""Implementaciones en memoria de los puertos, para las pruebas unitarias."""

import dataclasses
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime

from entrevecinos.application.users.ports import AccessToken
from entrevecinos.domain.communities.entities import (
    Community,
    Membership,
    MembershipDetail,
    MembershipRole,
    MembershipStatus,
    MemberSummary,
    MyMembership,
    NewCommunity,
)
from entrevecinos.domain.communities.errors import MembershipAlreadyExists
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


class InMemoryMembershipRepository:
    """Comparte las membresías con un `InMemoryCommunityRepository`."""

    def __init__(self, communities: InMemoryCommunityRepository) -> None:
        self.communities = communities
        self.memberships = communities.memberships

    def get(self, community_id: uuid.UUID, user_id: uuid.UUID) -> Membership | None:
        return self.memberships.get((community_id, user_id))

    def add_request(self, community_id: uuid.UUID, user_id: uuid.UUID) -> MembershipDetail:
        if existing := self.get(community_id, user_id):
            raise MembershipAlreadyExists(existing.status)
        membership = Membership(
            community_id=community_id,
            user_id=user_id,
            role=MembershipRole.MEMBER,
            status=MembershipStatus.PENDING,
            requested_at=datetime.now(UTC),
        )
        self.memberships[(community_id, user_id)] = membership
        return MembershipDetail(membership, MemberSummary(id=user_id, full_name="Vecino"))

    def list_for_user(
        self, user_id: uuid.UUID, status: MembershipStatus | None = None
    ) -> list[MyMembership]:
        return [
            MyMembership(m, self.communities.communities[m.community_id])
            for m in sorted(self.memberships.values(), key=lambda m: m.requested_at, reverse=True)
            if m.user_id == user_id and (status is None or m.status == status)
        ]


class InMemoryObjectStorage:
    def __init__(self, public_endpoint: str = "http://localhost:9000") -> None:
        self.public_endpoint = public_endpoint
        self.objects: dict[str, tuple[bytes, str]] = {}

    def put(self, key: str, data: bytes, content_type: str) -> None:
        self.objects[key] = (data, content_type)

    def presigned_get_url(self, key: str, expires_in: int) -> str:
        return f"{self.public_endpoint}/bucket/{key}?X-Amz-Expires={expires_in}&X-Amz-Signature=x"
