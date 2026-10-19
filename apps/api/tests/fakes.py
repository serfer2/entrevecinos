"""Implementaciones en memoria de los puertos, para las pruebas unitarias."""

import uuid
from datetime import UTC, datetime

from entrevecinos.application.users.ports import AccessToken
from entrevecinos.domain.users.entities import NewUser, PlatformRole, User
from entrevecinos.domain.users.errors import EmailAlreadyRegistered


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[uuid.UUID, User] = {}
        self.password_hashes: dict[uuid.UUID, str] = {}

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)

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
    def hash(self, password: str) -> str:
        return f"hashed:{password}"


class FakeTokenIssuer:
    def issue(self, user_id: uuid.UUID) -> AccessToken:
        return AccessToken(token=f"token-for:{user_id}", expires_in=3600)
