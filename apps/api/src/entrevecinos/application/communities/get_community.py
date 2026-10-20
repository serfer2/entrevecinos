import uuid

from entrevecinos.application.communities.ports import CommunityRepository
from entrevecinos.domain.communities.entities import Community
from entrevecinos.domain.communities.errors import CommunityNotFound


class GetCommunity:
    def __init__(self, communities: CommunityRepository) -> None:
        self._communities = communities

    def execute(self, community_id: uuid.UUID) -> Community:
        community = self._communities.get(community_id)
        if community is None:
            raise CommunityNotFound
        return community
