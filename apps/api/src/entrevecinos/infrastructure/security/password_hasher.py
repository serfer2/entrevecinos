from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


class Argon2PasswordHasher:
    """Hash Argon2id con los parámetros por defecto de pwdlib."""

    def __init__(self) -> None:
        self._password_hash = PasswordHash((Argon2Hasher(),))

    def hash(self, password: str) -> str:
        return self._password_hash.hash(password)
