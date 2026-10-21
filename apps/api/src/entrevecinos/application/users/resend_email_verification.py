from datetime import timedelta

from entrevecinos.application.users.email_verification import (
    Clock,
    EmailVerificationIssuer,
    utc_now,
)
from entrevecinos.application.users.ports import (
    EmailVerificationRepository,
    OutgoingEmail,
    UserRepository,
)
from entrevecinos.domain.users.value_objects import normalize_email

# Evita reenvíos en bucle: el último enlace tiene que tener al menos este tiempo.
RESEND_MIN_INTERVAL = timedelta(seconds=60)


class ResendEmailVerification:
    """Crea un enlace de validación nuevo para una cuenta pendiente y prepara su correo."""

    def __init__(
        self,
        users: UserRepository,
        verifications: EmailVerificationRepository,
        issuer: EmailVerificationIssuer,
        clock: Clock = utc_now,
    ) -> None:
        self._users = users
        self._verifications = verifications
        self._issuer = issuer
        self._clock = clock

    def execute(self, email: str) -> OutgoingEmail | None:
        """Correo a enviar, o `None` si no procede. El llamante no distingue los casos (HU-26)."""
        user = self._users.get_by_email(normalize_email(email))
        if user is None or not user.email_verification_pending:
            return None
        last = self._verifications.last_created_at(user.id)
        if last is not None and self._clock() - last < RESEND_MIN_INTERVAL:
            return None
        message, _ = self._issuer.issue(user)
        return message
