import uuid

from entrevecinos.application.authorization.community_access import (
    COMMUNITY_MANAGERS,
    CommunityAccess,
)
from entrevecinos.application.listings.ports import ListingRepository
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.listings.entities import Listing, ListingStatus
from entrevecinos.domain.listings.errors import ListingNotFound, ListingStatusConflict
from entrevecinos.domain.users.entities import User

# Moderación (HU-17): retirar desde un estado visible y restaurar a `active`.
RETIRABLE = frozenset({ListingStatus.ACTIVE, ListingStatus.RESERVED, ListingStatus.COMPLETED})


class ChangeListingStatus:
    """Cambios de estado de un anuncio. La moderación retira (`hidden`) y restaura (`active`)."""

    def __init__(self, access: CommunityAccess, listings: ListingRepository) -> None:
        self._access = access
        self._listings = listings

    def execute(self, user: User, listing_id: uuid.UUID, status: ListingStatus) -> Listing:
        listing = self._listings.get(listing_id)
        if listing is None:
            raise ListingNotFound
        if not self._access.has_role(user, listing.community_id, COMMUNITY_MANAGERS):
            raise PermissionDenied
        current = listing.status

        if status is ListingStatus.HIDDEN and current in RETIRABLE:
            return self._listings.set_status(listing_id, status, moderator_id=user.id)
        if status is ListingStatus.ACTIVE and current is ListingStatus.HIDDEN:
            return self._listings.set_status(listing_id, status, moderator_id=None)
        if status is current:
            raise ListingStatusConflict(ListingStatusConflict.SAME)
        raise ListingStatusConflict(ListingStatusConflict.NOT_ALLOWED)
