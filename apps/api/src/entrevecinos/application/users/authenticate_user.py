from dataclasses import dataclass

from entrevecinos.application.users.ports import (
    AccessToken,
    PasswordHasher,
    TokenIssuer,
    UserRepository,
)
from entrevecinos.domain.users.entities import User
from entrevecinos.domain.users.errors import EmailNotVerified, InvalidCredentials
from entrevecinos.domain.users.value_objects import normalize_email


@dataclass(frozen=True, slots=True)
class LoginCommand:
    email: str
    password: str


class AuthenticateUser:
    def __init__(self, users: UserRepository, hasher: PasswordHasher, tokens: TokenIssuer) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    def execute(self, command: LoginCommand) -> tuple[User, AccessToken]:
        credentials = self._users.get_credentials(normalize_email(command.email))
        user, password_hash = credentials if credentials else (None, None)

        # Se verifica siempre (con un hash ficticio si el correo no existe) para que el
        # tiempo de respuesta no revele qué correos están registrados.
        valid, new_hash = self._hasher.verify_and_update(command.password, password_hash)
        if user is None or not valid:
            raise InvalidCredentials
        # Solo se distingue tras comprobar la contraseña: no revela qué correos existen.
        if user.email_verification_pending:
            raise EmailNotVerified
        if not user.can_authenticate:
            raise InvalidCredentials

        if new_hash is not None:
            self._users.update_password_hash(user.id, new_hash)
        return user, self._tokens.issue(user.id)
