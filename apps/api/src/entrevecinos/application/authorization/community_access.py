import uuid
from collections.abc import Set

from entrevecinos.application.communities.ports import CommunityRepository, MembershipRepository
from entrevecinos.domain.communities.entities import Membership, MembershipRole
from entrevecinos.domain.communities.errors import CommunityNotFound, MembershipNotApproved
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.users.entities import PlatformRole, User


class CommunityAccess:
    """Única política de permisos por comunidad (comunidades, anuncios y administración).

    Comprueba primero que la comunidad existe (404): su existencia no es secreta.
    """

    def __init__(self, communities: CommunityRepository, memberships: MembershipRepository) -> None:
        self._communities = communities
        self._memberships = memberships

    def membership(self, user: User, community_id: uuid.UUID) -> Membership | None:
        """Membresía del usuario en una comunidad existente (en cualquier estado)."""
        if self._communities.get(community_id) is None:
            raise CommunityNotFound
        return self._memberships.get(community_id, user.id)

    def require_member(self, user: User, community_id: uuid.UUID) -> Membership | None:
        """Exige membresía aprobada. `platform_admin` pasa siempre (puede no tener membresía)."""
        membership = self.membership(user, community_id)
        if user.platform_role is PlatformRole.PLATFORM_ADMIN:
            return membership
        if membership is None:
            raise PermissionDenied
        if not membership.is_approved:
            raise MembershipNotApproved(membership.status)
        return membership

    def require_role(
        self, user: User, community_id: uuid.UUID, roles: Set[MembershipRole]
    ) -> Membership | None:
        """Exige membresía aprobada con uno de `roles`, o `platform_admin`."""
        membership = self.membership(user, community_id)
        if user.platform_role is PlatformRole.PLATFORM_ADMIN:
            return membership
        if membership is None or not membership.is_approved or membership.role not in roles:
            raise PermissionDenied
        return membership

    def has_role(self, user: User, community_id: uuid.UUID, roles: Set[MembershipRole]) -> bool:
        try:
            self.require_role(user, community_id, roles)
        except PermissionDenied:
            return False
        return True


COMMUNITY_MANAGERS = frozenset({MembershipRole.COMMUNITY_ADMIN, MembershipRole.MODERATOR})
COMMUNITY_ADMINS = frozenset({MembershipRole.COMMUNITY_ADMIN})
