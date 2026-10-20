import uuid

from entrevecinos.application.communities.ports import MembershipRepository
from entrevecinos.domain.communities.entities import MembershipStatus, MyMembership


class ListMyMemberships:
    def __init__(self, memberships: MembershipRepository) -> None:
        self._memberships = memberships

    def execute(
        self, user_id: uuid.UUID, status: MembershipStatus | None = None
    ) -> list[MyMembership]:
        return self._memberships.list_for_user(user_id, status)
