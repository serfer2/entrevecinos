from dataclasses import dataclass

from entrevecinos.application.users.ports import (
    AccessToken,
    PasswordHasher,
    TokenIssuer,
    UserRepository,
)
from entrevecinos.domain.users.entities import NewUser, User
from entrevecinos.domain.users.errors import EmailAlreadyRegistered
from entrevecinos.domain.users.value_objects import normalize_email


@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    email: str
    password: str
    full_name: str
    phone: str | None = None


class RegisterUser:
    def __init__(self, users: UserRepository, hasher: PasswordHasher, tokens: TokenIssuer) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    def execute(self, command: RegisterUserCommand) -> tuple[User, AccessToken]:
        email = normalize_email(command.email)
        if self._users.get_by_email(email) is not None:
            raise EmailAlreadyRegistered(email)

        user = self._users.add(
            NewUser(email=email, full_name=command.full_name, phone=command.phone),
            self._hasher.hash(command.password),
        )
        return user, self._tokens.issue(user.id)
