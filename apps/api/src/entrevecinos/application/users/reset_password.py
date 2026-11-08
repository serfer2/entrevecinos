from html import escape

from entrevecinos.application.mail.email_quota import EmailQuota
from entrevecinos.application.users.email_verification import Clock, hash_token, utc_now
from entrevecinos.application.users.ports import (
    OutgoingEmail,
    PasswordHasher,
    PasswordResetRepository,
    UserRepository,
)
from entrevecinos.domain.mail.errors import EmailQuotaExceeded
from entrevecinos.domain.mail.quota import QUOTA_TIMEZONE
from entrevecinos.domain.users.entities import User
from entrevecinos.domain.users.errors import PasswordResetExpired, PasswordResetInvalid


class ResetPassword:
    """Cambia la contraseña con el enlace del correo y prepara el aviso del cambio (HU-42).

    Cambiar la contraseña cierra las sesiones anteriores (`password_changed_at`) y valida el correo
    si estaba pendiente: el enlace demuestra que es suyo.
    """

    def __init__(
        self,
        users: UserRepository,
        resets: PasswordResetRepository,
        hasher: PasswordHasher,
        quota: EmailQuota,
        clock: Clock = utc_now,
    ) -> None:
        self._users = users
        self._resets = resets
        self._hasher = hasher
        self._quota = quota
        self._clock = clock

    def execute(self, token: str, password: str) -> OutgoingEmail | None:
        """Aviso del cambio a enviar, o `None` si no queda cupo de correos (el cambio se hace)."""
        reset = self._resets.get(hash_token(token))
        user = self._users.get_by_id(reset.user_id) if reset else None
        if reset is None or user is None or not user.can_reset_password:
            raise PasswordResetInvalid
        if reset.expires_at <= self._clock():
            raise PasswordResetExpired

        self._users.change_password(user.id, self._hasher.hash(password))
        if user.email_verified_at is None:
            self._users.mark_email_verified(user.id)
        self._resets.delete_for_user(user.id)
        return self._notice(user)

    def _notice(self, user: User) -> OutgoingEmail | None:
        try:
            self._quota.reserve()
        except EmailQuotaExceeded:
            # Ya queda registrado como error; el cambio que pide el usuario prima sobre el aviso.
            return None
        when = self._clock().astimezone(QUOTA_TIMEZONE).strftime("%d/%m/%Y a las %H:%M")
        text = (
            f"Hola, {user.full_name}:\n\n"
            f"La contraseña de tu cuenta de EntreVecinos se cambió el {when} (hora de Madrid).\n\n"
            "Si no has sido tú, pide un enlace nuevo desde «¿Has olvidado tu contraseña?» en el "
            "inicio de sesión y avisa a la administración de tu comunidad.\n"
        )
        html = (
            f"<p>Hola, {escape(user.full_name)}:</p>"
            "<p>La contraseña de tu cuenta de EntreVecinos se cambió el "
            f"{when} (hora de Madrid).</p>"
            "<p>Si no has sido tú, pide un enlace nuevo desde «¿Has olvidado tu contraseña?» en el "
            "inicio de sesión y avisa a la administración de tu comunidad.</p>"
        )
        return OutgoingEmail(
            to=user.email,
            subject="Tu contraseña de EntreVecinos ha cambiado",
            text=text,
            html=html,
        )
