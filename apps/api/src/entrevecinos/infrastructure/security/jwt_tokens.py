import uuid
from datetime import UTC, datetime, timedelta

import jwt

from entrevecinos.application.users.ports import AccessToken
from entrevecinos.domain.users.errors import NotAuthenticated

# Fijo en código: nunca se acepta `none` ni otro algoritmo elegido desde fuera.
ALGORITHM = "HS256"


class JwtTokenService:
    def __init__(self, secret: str, ttl_seconds: int) -> None:
        self._secret = secret
        self._ttl_seconds = ttl_seconds

    def issue(self, user_id: uuid.UUID) -> AccessToken:
        now = datetime.now(UTC)
        claims = {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(seconds=self._ttl_seconds),
        }
        token = jwt.encode(claims, self._secret, algorithm=ALGORITHM)
        return AccessToken(token=token, expires_in=self._ttl_seconds)

    def decode(self, token: str) -> uuid.UUID:
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=[ALGORITHM],
                options={"require": ["exp", "iat", "sub"]},
            )
            return uuid.UUID(claims["sub"])
        except (jwt.PyJWTError, ValueError) as error:
            raise NotAuthenticated from error
