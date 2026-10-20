from entrevecinos.domain.communities.entities import MembershipStatus
from entrevecinos.domain.errors import NotFoundError


class CommunityNotFound(NotFoundError):
    """La comunidad no existe o está desactivada."""


class MembershipAlreadyExists(Exception):
    """El usuario ya tiene una membresía (en cualquier estado) en la comunidad."""

    def __init__(self, status: MembershipStatus) -> None:
        super().__init__(f"Membership already exists with status {status}")
        self.status = status
