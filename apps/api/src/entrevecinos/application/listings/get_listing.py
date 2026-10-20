import uuid

from entrevecinos.application.listings.ports import ListingRepository
from entrevecinos.application.listings.visibility import ListingVisibility
from entrevecinos.domain.listings.entities import Listing
from entrevecinos.domain.listings.errors import ListingNotFound
from entrevecinos.domain.users.entities import User


class GetListing:
    def __init__(self, visibility: ListingVisibility, listings: ListingRepository) -> None:
        self._visibility = visibility
        self._listings = listings

    def execute(self, user: User, listing_id: uuid.UUID) -> Listing:
        listing = self._listings.get(listing_id)
        if listing is None:
            raise ListingNotFound
        self._visibility.require_visible(user, listing)
        return listing
