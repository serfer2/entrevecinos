import uuid
from dataclasses import dataclass

from entrevecinos.application.unset import UNSET
from entrevecinos.application.unset import Unset as _Unset
from entrevecinos.application.users.ports import UserRepository
from entrevecinos.domain.users.entities import User

__all__ = ["UNSET", "ProfileChanges", "UpdateProfile"]


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
