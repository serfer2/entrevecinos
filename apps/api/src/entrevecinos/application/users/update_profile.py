import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Final

from entrevecinos.application.users.ports import UserRepository
from entrevecinos.domain.users.entities import User


class _Unset(Enum):
    TOKEN = "UNSET"


UNSET: Final = _Unset.TOKEN
"""Campo no enviado: no se modifica (a diferencia de `None`, que borra el valor)."""


@dataclass(frozen=True, slots=True)
class ProfileChanges:
    full_name: str | _Unset = UNSET
    phone: str | None | _Unset = UNSET

    def as_values(self) -> dict[str, str | None]:
        """Solo los campos enviados."""
        values = {"full_name": self.full_name, "phone": self.phone}
        return {field: value for field, value in values.items() if value is not UNSET}


class UpdateProfile:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: uuid.UUID, changes: ProfileChanges) -> User:
        return self._users.update_profile(user_id, changes.as_values())
