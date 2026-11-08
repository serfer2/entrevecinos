import secrets
from datetime import timedelta
from html import escape

from entrevecinos.application.users.email_verification import Clock, hash_token, utc_now
from entrevecinos.application.users.ports import OutgoingEmail, PasswordResetRepository
from entrevecinos.domain.users.entities import User


class PasswordResetIssuer:
    """Crea el enlace para restablecer la contraseña y prepara el mensaje que lo contiene."""

    def __init__(
        self,
        resets: PasswordResetRepository,
        web_public_url: str,
        ttl: timedelta,
        clock: Clock = utc_now,
    ) -> None:
        self._resets = resets
        self._web_public_url = web_public_url.rstrip("/")
        self._ttl = ttl
        self._clock = clock

    def issue(self, user: User) -> OutgoingEmail:
        """Mensaje con el enlace nuevo. Los enlaces anteriores del usuario dejan de valer."""
        token = secrets.token_urlsafe(32)
        self._resets.replace(user.id, hash_token(token), self._clock() + self._ttl)
        link = f"{self._web_public_url}/restablecer-contrasena/enlace?token={token}"
        return self._message(user, link)

    def _message(self, user: User, link: str) -> OutgoingEmail:
        minutes = int(self._ttl.total_seconds() // 60)
        text = (
            f"Hola, {user.full_name}:\n\n"
            "Hemos recibido una petición para restablecer la contraseña de tu cuenta de "
            "EntreVecinos. Para elegir una contraseña nueva, abre este enlace:\n\n"
            f"{link}\n\n"
            f"El enlace caduca en {minutes} minutos.\n\n"
            "Si no lo has pedido tú, ignora este mensaje: tu contraseña no cambiará.\n"
        )
        html = (
            f"<p>Hola, {escape(user.full_name)}:</p>"
            "<p>Hemos recibido una petición para restablecer la contraseña de tu cuenta de "
            "EntreVecinos. Para elegir una contraseña nueva, pulsa el siguiente enlace:</p>"
            f'<p><a href="{escape(link)}">Elegir una contraseña nueva</a></p>'
            f"<p>El enlace caduca en {minutes} minutos.</p>"
            "<p>Si no lo has pedido tú, ignora este mensaje: tu contraseña no cambiará.</p>"
        )
        return OutgoingEmail(
            to=user.email,
            subject="Restablece tu contraseña de EntreVecinos",
            text=text,
            html=html,
        )
