import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from entrevecinos.domain.users.entities import EmailVerification, NewUser, User


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
        """Guarda el usuario inactivo y sin validar su correo.

        Lanza `EmailAlreadyRegistered` si el correo ya existe.
        """
        ...

    def mark_email_verified(self, user_id: uuid.UUID) -> User:
        """Marca el correo como validado y activa la cuenta."""
        ...

    def update_password_hash(self, user_id: uuid.UUID, password_hash: str) -> None: ...

    def update_profile(self, user_id: uuid.UUID, values: Mapping[str, str | None]) -> User:
        """Actualiza solo los campos de `values` (`full_name`, `phone`)."""
        ...


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


class EmailVerificationRepository(Protocol):
    def replace(self, user_id: uuid.UUID, token_hash: str, expires_at: datetime) -> None:
        """Guarda el enlace nuevo y marca los anteriores como sustituidos: solo vale el último."""
        ...

    def get(self, token_hash: str) -> EmailVerification | None: ...

    def last_created_at(self, user_id: uuid.UUID) -> datetime | None:
        """Fecha del enlace más reciente del usuario, o `None` si no tiene ninguno."""
        ...

    def mark_used(self, token_hash: str) -> None:
        """Marca el enlace como usado y los demás vigentes de su usuario como sustituidos."""
        ...


@dataclass(frozen=True, slots=True)
class OutgoingEmail:
    to: str
    subject: str
    text: str
    html: str


class EmailSender(Protocol):
    def send(self, email: OutgoingEmail) -> None:
        """Envía el correo. Lanza una excepción si el servidor no lo acepta."""
        ...
