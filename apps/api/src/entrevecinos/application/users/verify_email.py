from entrevecinos.application.users.email_verification import Clock, hash_token, utc_now
from entrevecinos.application.users.ports import (
    AccessToken,
    EmailVerificationRepository,
    TokenIssuer,
    UserRepository,
)
from entrevecinos.domain.users.entities import User
from entrevecinos.domain.users.errors import (
    EmailAlreadyVerified,
    VerificationExpired,
    VerificationInvalid,
    VerificationSuperseded,
)


class VerifyEmail:
    """Valida el correo con el token del enlace, activa la cuenta e inicia la sesión."""

    def __init__(
        self,
        users: UserRepository,
        verifications: EmailVerificationRepository,
        tokens: TokenIssuer,
        clock: Clock = utc_now,
    ) -> None:
        self._users = users
        self._verifications = verifications
        self._tokens = tokens
        self._clock = clock

    def execute(self, token: str) -> tuple[User, AccessToken]:
        token_hash = hash_token(token)
        verification = self._verifications.get(token_hash)
        user = self._users.get_by_id(verification.user_id) if verification else None
        if verification is None or user is None or user.deleted_at is not None:
            raise VerificationInvalid
        # Manda el estado de la cuenta: validada, cualquier enlace suyo responde igual (HU-27).
        if user.email_verified_at is not None:
            raise EmailAlreadyVerified
        # La sustitución va antes que la caducidad: el usuario debe usar el último correo.
        if verification.superseded_at is not None:
            raise VerificationSuperseded(user.email)
        if verification.used_at is not None:
            raise VerificationInvalid
        if verification.expires_at <= self._clock():
            raise VerificationExpired(user.email)

        user = self._users.mark_email_verified(user.id)
        self._verifications.mark_used(token_hash)
        return user, self._tokens.issue(user.id)
