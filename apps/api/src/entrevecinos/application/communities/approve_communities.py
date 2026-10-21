import uuid

from entrevecinos.application.communities.ports import CommunityRepository
from entrevecinos.application.pagination import PageRequest, PageResult
from entrevecinos.domain.communities.entities import Community
from entrevecinos.domain.communities.errors import CommunityNotFound
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.users.entities import PlatformRole, User


def _require_platform_admin(user: User) -> None:
    if user.platform_role is not PlatformRole.PLATFORM_ADMIN:
        raise PermissionDenied


class ListAllCommunities:
    """Listado de administración: incluye las comunidades pendientes de aprobación."""

    def __init__(self, communities: CommunityRepository) -> None:
        self._communities = communities

    def execute(
        self, user: User, is_active: bool | None, page: PageRequest
    ) -> PageResult[Community]:
        _require_platform_admin(user)
        return self._communities.list_all(is_active, page)


class ApproveCommunity:
    """Activa una comunidad pendiente. Aprobar una ya activa no cambia nada."""

    def __init__(self, communities: CommunityRepository) -> None:
        self._communities = communities

    def execute(self, user: User, community_id: uuid.UUID) -> Community:
        _require_platform_admin(user)
        community = self._communities.activate(community_id)
        if community is None:
            raise CommunityNotFound
        return community
