from entrevecinos.application.users.ports import TokenClaims, UserRepository
from entrevecinos.domain.users.entities import User
from entrevecinos.domain.users.errors import NotAuthenticated


class GetCurrentUser:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, claims: TokenClaims) -> User:
        user = self._users.get_by_id(claims.user_id)
        if user is None or not user.can_authenticate:
            raise NotAuthenticated
        # Cambiar la contraseña cierra las sesiones anteriores (TK-102). `iat` va en segundos
        # enteros: se trunca la fecha del cambio para no rechazar un token del mismo segundo.
        changed_at = user.password_changed_at
        if changed_at is not None and claims.issued_at < changed_at.replace(microsecond=0):
            raise NotAuthenticated
        return user
