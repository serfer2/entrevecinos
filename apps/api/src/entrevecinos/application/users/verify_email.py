from entrevecinos.application.users.email_verification import Clock, hash_token, utc_now
from entrevecinos.application.users.ports import (
    AccessToken,
    EmailVerificationRepository,
    TokenIssuer,
    UserRepository,
)
from entrevecinos.domain.users.entities import User
from entrevecinos.domain.users.errors import VerificationExpired, VerificationInvalid


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
        verification = self._verifications.get(hash_token(token))
        user = self._users.get_by_id(verification.user_id) if verification else None
        if verification is None or user is None or user.deleted_at is not None:
            raise VerificationInvalid
        if verification.expires_at <= self._clock():
            raise VerificationExpired(user.email)

        user = self._users.mark_email_verified(user.id)
        self._verifications.delete_for_user(user.id)
        return user, self._tokens.issue(user.id)
