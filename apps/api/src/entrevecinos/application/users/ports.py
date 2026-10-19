import uuid
from dataclasses import dataclass
from typing import Protocol

from entrevecinos.domain.users.entities import NewUser, User


@dataclass(frozen=True, slots=True)
class AccessToken:
    token: str
    expires_in: int


class UserRepository(Protocol):
    def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...

    def get_credentials(self, email: str) -> tuple[User, str] | None:
        """Usuario y hash de su contraseña, o `None` si el correo no existe."""
        ...

    def add(self, user: NewUser, password_hash: str) -> User:
        """Guarda el usuario. Lanza `EmailAlreadyRegistered` si el correo ya existe."""
        ...

    def update_password_hash(self, user_id: uuid.UUID, password_hash: str) -> None: ...


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify_and_update(
        self, password: str, password_hash: str | None
    ) -> tuple[bool, str | None]:
        """Comprueba la contraseña y devuelve un hash nuevo si el actual usa parámetros antiguos.

        Con `password_hash=None` verifica contra un hash ficticio (mismo coste) y devuelve `False`.
        """
        ...


class TokenIssuer(Protocol):
    def issue(self, user_id: uuid.UUID) -> AccessToken: ...


class TokenService(TokenIssuer, Protocol):
    def decode(self, token: str) -> uuid.UUID:
        """Id del usuario del token. Lanza `NotAuthenticated` si el token no es válido."""
        ...
