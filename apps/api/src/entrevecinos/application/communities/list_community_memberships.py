import uuid

from entrevecinos.application.authorization.community_access import (
    COMMUNITY_MANAGERS,
    CommunityAccess,
)
from entrevecinos.application.communities.ports import MembershipRepository
from entrevecinos.application.pagination import PageRequest, PageResult
from entrevecinos.domain.communities.entities import MembershipDetail, MembershipStatus
from entrevecinos.domain.users.entities import User


class ListCommunityMemberships:
    def __init__(self, access: CommunityAccess, memberships: MembershipRepository) -> None:
        self._access = access
        self._memberships = memberships

    def execute(
        self,
        user: User,
        community_id: uuid.UUID,
        status: MembershipStatus | None,
        page: PageRequest,
    ) -> PageResult[MembershipDetail]:
        self._access.require_role(user, community_id, COMMUNITY_MANAGERS)
        return self._memberships.list_for_community(community_id, status, page)
