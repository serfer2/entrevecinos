from datetime import timedelta

from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.application.users.email_verification import Clock, utc_now
from entrevecinos.application.users.password_reset import PasswordResetIssuer
from entrevecinos.application.users.ports import (
    OutgoingEmail,
    PasswordResetRepository,
    UserRepository,
)
from entrevecinos.domain.users.value_objects import normalize_email

# Evita bombardear un buzón: el último enlace tiene que tener al menos este tiempo.
REQUEST_MIN_INTERVAL = timedelta(seconds=60)


class RequestPasswordReset:
    """Crea un enlace para restablecer la contraseña y prepara su correo (HU-41)."""

    def __init__(
        self,
        users: UserRepository,
        resets: PasswordResetRepository,
        issuer: PasswordResetIssuer,
        quota: EmailQuota,
        clock: Clock = utc_now,
    ) -> None:
        self._users = users
        self._resets = resets
        self._issuer = issuer
        self._quota = quota
        self._clock = clock

    def execute(self, email: str) -> OutgoingEmail | None:
        """Correo a enviar, o `None` si no procede. El llamante no distingue los casos.

        Sin cupo de correos (TK-099) lanza `EmailQuotaExceeded` antes de buscar la cuenta, para
        responder igual exista o no.
        """
        self._quota.ensure_available()
        user = self._users.get_by_email(normalize_email(email))
        if user is None or not user.can_reset_password:
            return None
        last = self._resets.last_created_at(user.id)
        if last is not None and self._clock() - last < REQUEST_MIN_INTERVAL:
            return None
        self._quota.reserve()
        return self._issuer.issue(user)
