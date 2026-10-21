from entrevecinos.application.communities.ports import CommunityRepository
from entrevecinos.domain.communities.entities import Community, NewCommunity
from entrevecinos.domain.communities.errors import PendingCommunityExists
from entrevecinos.domain.users.entities import PlatformRole, User


class CreateCommunity:
    def __init__(self, communities: CommunityRepository) -> None:
        self._communities = communities

    def execute(self, community: NewCommunity, creator: User) -> Community:
        """El creador queda como administrador de la comunidad, con el acceso aprobado.

        La comunidad queda pendiente (inactiva) hasta que un `platform_admin` la apruebe, salvo
        que la cree un `platform_admin`: entonces queda activa al momento. Cada usuario puede tener
        solo una comunidad pendiente.
        """
        is_active = creator.platform_role is PlatformRole.PLATFORM_ADMIN
        if not is_active and self._communities.has_pending(creator.id):
            raise PendingCommunityExists
        return self._communities.add(community, admin_id=creator.id, is_active=is_active)
