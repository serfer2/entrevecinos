from entrevecinos.application.authorization.community_access import CommunityAccess
from entrevecinos.application.listings.ports import ListingQuery, ListingRepository
from entrevecinos.application.pagination import PageResult
from entrevecinos.domain.listings.entities import Listing
from entrevecinos.domain.users.entities import User


class ListCommunityListings:
    def __init__(self, access: CommunityAccess, listings: ListingRepository) -> None:
        self._access = access
        self._listings = listings

    def execute(self, user: User, query: ListingQuery) -> PageResult[Listing]:
        self._access.require_member(user, query.community_id)
        return self._listings.search(query)
