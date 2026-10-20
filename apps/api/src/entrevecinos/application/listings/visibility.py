from entrevecinos.application.authorization.community_access import (
    COMMUNITY_MANAGERS,
    CommunityAccess,
)
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.listings.entities import Listing, ListingStatus
from entrevecinos.domain.listings.errors import ListingNotFound
from entrevecinos.domain.users.entities import User

# Estados que solo ven el autor y la gestión de la comunidad.
RESTRICTED_STATUSES = frozenset({ListingStatus.HIDDEN, ListingStatus.DRAFT})


class ListingVisibility:
    """Única regla de visibilidad de un anuncio: detalle, imágenes y edición.

    El orden evita filtrar información: el anuncio ya existe y no está eliminado (lo garantiza
    el repositorio, si no es 404); después, membresía aprobada (403); por último, un anuncio
    retirado, o de un autor bloqueado o expulsado, solo para su autor y los gestores (404 para
    el resto: no se revela que existe).
    """

    def __init__(self, access: CommunityAccess) -> None:
        self._access = access

    def require_visible(self, user: User, listing: Listing) -> None:
        self._access.require_member(user, listing.community_id)
        restricted = listing.status in RESTRICTED_STATUSES or not listing.owner_is_member
        if restricted and not self.is_owner_or_manager(user, listing):
            raise ListingNotFound

    def is_owner_or_manager(self, user: User, listing: Listing) -> bool:
        return listing.owner.id == user.id or self._access.has_role(
            user, listing.community_id, COMMUNITY_MANAGERS
        )

    def can_view(self, user: User, listing: Listing) -> bool:
        try:
            self.require_visible(user, listing)
        except (ListingNotFound, PermissionDenied):
            return False
        return True
