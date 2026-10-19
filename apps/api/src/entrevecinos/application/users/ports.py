import uuid
from dataclasses import dataclass
from typing import Protocol

from entrevecinos.domain.users.entities import NewUser, User


@dataclass(frozen=True, slots=True)
class AccessToken:
    token: str
    expires_in: int


class UserRepository(Protocol):
    def get_by_email(self, email: str) -> User | None: ...

    def add(self, user: NewUser, password_hash: str) -> User:
        """Guarda el usuario. Lanza `EmailAlreadyRegistered` si el correo ya existe."""
        ...


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...


class TokenIssuer(Protocol):
    def issue(self, user_id: uuid.UUID) -> AccessToken: ...
