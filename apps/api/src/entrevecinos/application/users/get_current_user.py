import uuid

from entrevecinos.application.users.ports import UserRepository
from entrevecinos.domain.users.entities import User
from entrevecinos.domain.users.errors import NotAuthenticated


class GetCurrentUser:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: uuid.UUID) -> User:
        user = self._users.get_by_id(user_id)
        if user is None or not user.can_authenticate:
            raise NotAuthenticated
        return user
