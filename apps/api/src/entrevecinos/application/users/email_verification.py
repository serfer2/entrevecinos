import hashlib
import secrets
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from html import escape

from entrevecinos.application.users.ports import EmailVerificationRepository, OutgoingEmail
from entrevecinos.domain.users.entities import User

Clock = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(UTC)


def hash_token(token: str) -> str:
    """SHA-256 del token: lo único que se guarda, para que una copia de la BD no sirva de nada."""
    return hashlib.sha256(token.encode()).hexdigest()


class EmailVerificationIssuer:
    """Crea el enlace de validación del correo y prepara el mensaje que lo contiene."""

    def __init__(
        self,
        verifications: EmailVerificationRepository,
        web_public_url: str,
        ttl: timedelta,
        clock: Clock = utc_now,
    ) -> None:
        self._verifications = verifications
        self._web_public_url = web_public_url.rstrip("/")
        self._ttl = ttl
        self._clock = clock

    def issue(self, user: User) -> tuple[OutgoingEmail, datetime]:
        """Mensaje con el enlace nuevo y su caducidad. Los enlaces anteriores dejan de valer."""
        token = secrets.token_urlsafe(32)
        expires_at = self._clock() + self._ttl
        self._verifications.replace(user.id, hash_token(token), expires_at)
        link = f"{self._web_public_url}/verificar-correo?token={token}"
        return self._message(user, link), expires_at

    def _message(self, user: User, link: str) -> OutgoingEmail:
        hours = int(self._ttl.total_seconds() // 3600)
        text = (
            f"Hola, {user.full_name}:\n\n"
            "Gracias por registrarte en EntreVecinos. Para activar tu cuenta, abre este enlace:\n\n"
            f"{link}\n\n"
            f"El enlace caduca en {hours} horas.\n\n"
            "Si no te has registrado tú, ignora este mensaje.\n"
        )
        html = (
            f"<p>Hola, {escape(user.full_name)}:</p>"
            "<p>Gracias por registrarte en EntreVecinos. Para activar tu cuenta, "
            "pulsa el siguiente enlace:</p>"
            f'<p><a href="{escape(link)}">Validar mi correo electrónico</a></p>'
            f"<p>El enlace caduca en {hours} horas.</p>"
            "<p>Si no te has registrado tú, ignora este mensaje.</p>"
        )
        return OutgoingEmail(
            to=user.email, subject="Valida tu correo en EntreVecinos", text=text, html=html
        )
