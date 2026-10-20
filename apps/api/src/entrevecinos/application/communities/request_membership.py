import uuid

from entrevecinos.application.communities.ports import CommunityRepository, MembershipRepository
from entrevecinos.domain.communities.entities import MembershipDetail
from entrevecinos.domain.communities.errors import CommunityNotFound, MembershipAlreadyExists


class RequestMembership:
    def __init__(self, communities: CommunityRepository, memberships: MembershipRepository) -> None:
        self._communities = communities
        self._memberships = memberships

    def execute(self, community_id: uuid.UUID, user_id: uuid.UUID) -> MembershipDetail:
        if self._communities.get(community_id) is None:
            raise CommunityNotFound
        existing = self._memberships.get(community_id, user_id)
        if existing is not None:
            raise MembershipAlreadyExists(existing.status)
        return self._memberships.add_request(community_id, user_id)
