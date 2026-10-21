from entrevecinos.domain.communities.entities import MembershipStatus
from entrevecinos.domain.errors import NotFoundError, PermissionDenied


class CommunityNotFound(NotFoundError):
    """La comunidad no existe o está desactivada."""


class PendingCommunityExists(Exception):
    """El usuario ya tiene una comunidad pendiente de aprobación: no puede crear otra."""


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


class MembershipChangeRejected(Exception):
    """El cambio de la membresía choca con su estado o con las reglas de la comunidad (409)."""

    CANNOT_BLOCK_ADMIN = "No se puede bloquear a un administrador de la comunidad."
    CANNOT_CHANGE_SELF = "No puedes cambiar el estado de tu propia membresía."
    NOT_ALLOWED = "Cambio de estado no permitido."
    LAST_ADMIN = "La comunidad debe tener al menos un administrador."

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail
