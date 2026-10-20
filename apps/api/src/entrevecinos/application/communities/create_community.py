import uuid

from entrevecinos.application.communities.ports import CommunityRepository
from entrevecinos.domain.communities.entities import Community, NewCommunity


class CreateCommunity:
    def __init__(self, communities: CommunityRepository) -> None:
        self._communities = communities

    def execute(self, community: NewCommunity, creator_id: uuid.UUID) -> Community:
        """El creador queda como administrador de la comunidad, con el acceso aprobado."""
        return self._communities.add(community, admin_id=creator_id)
