from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


class Argon2PasswordHasher:
    """Hash Argon2id con los parámetros por defecto de pwdlib."""

    def __init__(self) -> None:
        self._password_hash = PasswordHash((Argon2Hasher(),))
        # Se verifica contra este hash cuando el correo no existe, con el mismo coste.
        self._dummy_hash = self._password_hash.hash("entrevecinos-dummy-password")

    def hash(self, password: str) -> str:
        return self._password_hash.hash(password)

    def verify_and_update(
        self, password: str, password_hash: str | None
    ) -> tuple[bool, str | None]:
        if password_hash is None:
            self._password_hash.verify(password, self._dummy_hash)
            return False, None
        return self._password_hash.verify_and_update(password, password_hash)
