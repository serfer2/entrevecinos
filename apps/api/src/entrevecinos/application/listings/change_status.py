import uuid

from entrevecinos.application.authorization.community_access import (
    COMMUNITY_MANAGERS,
    CommunityAccess,
)
from entrevecinos.application.listings.ports import ListingRepository
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.listings.entities import Listing, ListingStatus
from entrevecinos.domain.listings.errors import (
    ListingLocked,
    ListingNotFound,
    ListingStatusConflict,
)
from entrevecinos.domain.users.entities import User

Status = ListingStatus

# Moderación (HU-17): retirar desde un estado visible y restaurar a `active`.
RETIRABLE = frozenset({Status.ACTIVE, Status.RESERVED, Status.COMPLETED})

# Autor (HU-09b): reservar, quitar la reserva y finalizar. `completed` es un estado final.
AUTHOR_TRANSITIONS = frozenset(
    {
        (Status.ACTIVE, Status.RESERVED),
        (Status.RESERVED, Status.ACTIVE),
        (Status.ACTIVE, Status.COMPLETED),
        (Status.RESERVED, Status.COMPLETED),
    }
)


def is_moderation(current: ListingStatus, status: ListingStatus) -> bool:
    return (status is Status.HIDDEN and current in RETIRABLE) or (
        status is Status.ACTIVE and current is Status.HIDDEN
    )


class ChangeListingStatus:
    """Cambios de estado de un anuncio.

    - La gestión de la comunidad retira (`hidden`) y restaura (`active`).
    - El autor reserva, quita la reserva y finaliza su anuncio.

    `active` es ambiguo (restaurar o quitar la reserva): lo decide el estado actual.
    """

    def __init__(self, access: CommunityAccess, listings: ListingRepository) -> None:
        self._access = access
        self._listings = listings

    def execute(self, user: User, listing_id: uuid.UUID, status: ListingStatus) -> Listing:
        listing = self._listings.get(listing_id)
        if listing is None:
            raise ListingNotFound
        current = listing.status
        is_owner = listing.owner.id == user.id
        is_manager = self._access.has_role(user, listing.community_id, COMMUNITY_MANAGERS)
        if not is_owner and not is_manager:
            raise PermissionDenied

        if is_manager and is_moderation(current, status):
            moderator_id = user.id if status is Status.HIDDEN else None
            return self._listings.set_status(listing_id, status, moderator_id=moderator_id)

        if is_owner:
            # Un autor bloqueado o expulsado ya no gestiona sus anuncios.
            self._access.require_member(user, listing.community_id)
            if current is Status.HIDDEN:
                raise ListingLocked(ListingLocked.RETIRED)
            if (current, status) in AUTHOR_TRANSITIONS:
                return self._listings.set_status(listing_id, status, moderator_id=None)
        elif status in (Status.RESERVED, Status.COMPLETED):
            # Reservar o finalizar es una decisión del autor, no de la moderación.
            raise PermissionDenied

        if status is current:
            raise ListingStatusConflict(ListingStatusConflict.SAME)
        if current is Status.COMPLETED:
            raise ListingStatusConflict(ListingStatusConflict.COMPLETED_FINAL)
        if status is Status.HIDDEN:
            raise PermissionDenied
        raise ListingStatusConflict(ListingStatusConflict.NOT_ALLOWED)
