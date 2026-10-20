from entrevecinos.domain.communities.entities import MembershipStatus
from entrevecinos.domain.errors import NotFoundError, PermissionDenied


class CommunityNotFound(NotFoundError):
    """La comunidad no existe o está desactivada."""


class MembershipAlreadyExists(Exception):
    """El usuario ya tiene una membresía (en cualquier estado) en la comunidad."""

    def __init__(self, status: MembershipStatus) -> None:
        super().__init__(f"Membership already exists with status {status}")
        self.status = status


class MembershipNotFound(NotFoundError):
    """El usuario no tiene membresía en la comunidad."""


class MembershipNotApproved(PermissionDenied):
    """El usuario tiene membresía en la comunidad, pero no está aprobada."""

    def __init__(self, status: MembershipStatus) -> None:
        super().__init__(f"Membership not approved: {status}")
        self.status = status


class MembershipAlreadyReviewed(Exception):
    """La solicitud ya se aprobó o rechazó: no admite otra revisión."""
