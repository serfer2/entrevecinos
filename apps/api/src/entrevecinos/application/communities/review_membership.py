import uuid

from entrevecinos.application.authorization.community_access import (
    COMMUNITY_ADMINS,
    CommunityAccess,
)
from entrevecinos.application.communities.ports import MembershipRepository
from entrevecinos.domain.communities.entities import (
    MembershipDetail,
    MembershipRole,
    MembershipStatus,
)
from entrevecinos.domain.communities.errors import (
    MembershipAlreadyReviewed,
    MembershipChangeRejected,
    MembershipNotFound,
)
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.users.entities import PlatformRole, User

REVIEW_RESULTS = frozenset({MembershipStatus.APPROVED, MembershipStatus.REJECTED})

# Transiciones de la gestión de miembros (TK-040), además de la revisión de solicitudes.
MANAGEMENT_TRANSITIONS = frozenset(
    {
        (MembershipStatus.APPROVED, MembershipStatus.BLOCKED),  # bloquear
        (MembershipStatus.BLOCKED, MembershipStatus.APPROVED),  # desbloquear
    }
)


class ChangeMembershipStatus:
    """Revisa solicitudes (`pending → approved | rejected`) y bloquea o desbloquea miembros."""

    def __init__(self, access: CommunityAccess, memberships: MembershipRepository) -> None:
        self._access = access
        self._memberships = memberships

    def execute(
        self, admin: User, community_id: uuid.UUID, user_id: uuid.UUID, status: MembershipStatus
    ) -> MembershipDetail:
        self._access.require_role(admin, community_id, COMMUNITY_ADMINS)
        membership = self._memberships.get(community_id, user_id)
        if membership is None:
            raise MembershipNotFound

        current = membership.status
        if current is MembershipStatus.PENDING:
            if status not in REVIEW_RESULTS:
                raise MembershipChangeRejected(MembershipChangeRejected.NOT_ALLOWED)
        elif (current, status) in MANAGEMENT_TRANSITIONS:
            if status is MembershipStatus.BLOCKED:
                if user_id == admin.id:
                    raise MembershipChangeRejected(MembershipChangeRejected.CANNOT_CHANGE_SELF)
                if membership.role is MembershipRole.COMMUNITY_ADMIN:
                    raise MembershipChangeRejected(MembershipChangeRejected.CANNOT_BLOCK_ADMIN)
        elif status in REVIEW_RESULTS and current in REVIEW_RESULTS:
            raise MembershipAlreadyReviewed
        else:
            raise MembershipChangeRejected(MembershipChangeRejected.NOT_ALLOWED)

        return self._memberships.review(community_id, user_id, status, admin.id)


class RemoveMembership:
    """Expulsión (un administrador elimina la membresía de otro) o salida (la propia).

    A diferencia del bloqueo, tras la expulsión el vecino puede volver a solicitar el acceso.
    """

    def __init__(self, access: CommunityAccess, memberships: MembershipRepository) -> None:
        self._access = access
        self._memberships = memberships

    def execute(self, actor: User, community_id: uuid.UUID, user_id: uuid.UUID) -> None:
        own = actor.id == user_id
        if own:
            self._access.membership(actor, community_id)  # 404 si la comunidad no existe
        else:
            self._access.require_role(actor, community_id, COMMUNITY_ADMINS)

        membership = self._memberships.get(community_id, user_id)
        if membership is None:
            raise MembershipNotFound
        target_is_admin = (
            membership.role is MembershipRole.COMMUNITY_ADMIN
            and membership.status is MembershipStatus.APPROVED
        )
        platform_admin = actor.platform_role is PlatformRole.PLATFORM_ADMIN
        if not own and target_is_admin and not platform_admin:
            raise PermissionDenied
        if target_is_admin and self._memberships.count_admins(community_id) <= 1:
            raise MembershipChangeRejected(MembershipChangeRejected.LAST_ADMIN)
        self._memberships.delete(community_id, user_id)
