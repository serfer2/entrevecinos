import uuid

from entrevecinos.application.authorization.community_access import (
    COMMUNITY_MANAGERS,
    CommunityAccess,
)
from entrevecinos.application.listings.ports import ListingRepository
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.listings.errors import ListingNotFound
from entrevecinos.domain.users.entities import User


class DeleteListing:
    """Borrado lógico: el autor (siempre) o la gestión de la comunidad."""

    def __init__(self, access: CommunityAccess, listings: ListingRepository) -> None:
        self._access = access
        self._listings = listings

    def execute(self, user: User, listing_id: uuid.UUID) -> None:
        listing = self._listings.get(listing_id)
        if listing is None:
            raise ListingNotFound
        if listing.owner.id != user.id and not self._access.has_role(
            user, listing.community_id, COMMUNITY_MANAGERS
        ):
            raise PermissionDenied
        self._listings.soft_delete(listing_id)
