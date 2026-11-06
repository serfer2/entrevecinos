from dataclasses import dataclass
from datetime import datetime

from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.application.users.email_verification import EmailVerificationIssuer
from entrevecinos.application.users.ports import OutgoingEmail, PasswordHasher, UserRepository
from entrevecinos.domain.users.entities import NewUser, User
from entrevecinos.domain.users.errors import EmailAlreadyRegistered, EmailPendingVerification
from entrevecinos.domain.users.value_objects import normalize_email


@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    email: str
    password: str
    full_name: str
    phone: str | None = None


@dataclass(frozen=True, slots=True)
class Registration:
    """Cuenta creada, pendiente de validar, y el correo con el enlace que hay que enviar."""

    user: User
    verification_email: OutgoingEmail
    verification_expires_at: datetime


class RegisterUser:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        verification: EmailVerificationIssuer,
        quota: EmailQuota,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._verification = verification
        self._quota = quota

    def execute(self, command: RegisterUserCommand) -> Registration:
        email = normalize_email(command.email)
        existing = self._users.get_by_email(email)
        if existing is not None:
            # Los datos del segundo intento se descartan: la cuenta pendiente no cambia.
            if existing.email_verification_pending:
                raise EmailPendingVerification(email)
            raise EmailAlreadyRegistered(email)

        # Sin cupo de correos (TK-099) no se crea la cuenta: no se podría validar. La plaza se
        # reserva en la misma transacción, así que un fallo posterior la devuelve.
        self._quota.reserve()
        user = self._users.add(
            NewUser(email=email, full_name=command.full_name, phone=command.phone),
            self._hasher.hash(command.password),
        )
        message, expires_at = self._verification.issue(user)
        return Registration(user, message, expires_at)
