import uuid
from datetime import UTC, datetime

import pytest

from entrevecinos.application.listings.delete_listing import DeleteListing
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.listings.entities import Listing, ListingOwner, ListingStatus, ListingType
from entrevecinos.domain.listings.errors import ListingNotFound
from tests.test_community_access import make_user


def make_listing(owner_id: uuid.UUID) -> Listing:
    now = datetime.now(UTC)
    return Listing(
        id=uuid.uuid4(),
        community_id=uuid.uuid4(),
        owner=ListingOwner(id=owner_id, full_name="Autor", phone=None, email="a@b.c"),
        category_id=uuid.uuid4(),
        title="Bicicleta",
        description="Poco uso",
        type=ListingType.SELL,
        price=None,
        currency=None,
        status=ListingStatus.ACTIVE,
        published_at=now,
        updated_at=now,
    )


class Listings:
    def __init__(self, listing: Listing | None) -> None:
        self.listing = listing
        self.deleted: list[uuid.UUID] = []

    def get(self, listing_id):
        return self.listing if self.listing and self.listing.id == listing_id else None

    def soft_delete(self, listing_id):
        self.deleted.append(listing_id)


class Access:
    def __init__(self, manager: bool) -> None:
        self.manager = manager

    def has_role(self, user, community_id, roles):
        return self.manager


def test_author_can_delete_even_without_role() -> None:
    author = make_user()
    listing = make_listing(author.id)
    listings = Listings(listing)

    DeleteListing(Access(manager=False), listings).execute(author, listing.id)

    assert listings.deleted == [listing.id]


def test_manager_can_delete_others() -> None:
    listing = make_listing(uuid.uuid4())
    listings = Listings(listing)

    DeleteListing(Access(manager=True), listings).execute(make_user(), listing.id)

    assert listings.deleted == [listing.id]


def test_others_are_denied_and_missing_is_not_found() -> None:
    listing = make_listing(uuid.uuid4())
    listings = Listings(listing)

    with pytest.raises(PermissionDenied):
        DeleteListing(Access(manager=False), listings).execute(make_user(), listing.id)
    with pytest.raises(ListingNotFound):
        DeleteListing(Access(manager=True), listings).execute(make_user(), uuid.uuid4())
    assert listings.deleted == []


def test_list_community_listings_requires_membership_first() -> None:
    from entrevecinos.application.listings.list_community_listings import ListCommunityListings
    from entrevecinos.application.listings.ports import ListingQuery
    from entrevecinos.application.pagination import PageRequest, PageResult

    calls: list[str] = []

    class Gate:
        def require_member(self, user, community_id):
            calls.append("access")
            raise PermissionDenied

    class Repo:
        def search(self, query):
            calls.append("search")
            return PageResult(items=[], total=0)

    query = ListingQuery(community_id=uuid.uuid4(), page=PageRequest())
    with pytest.raises(PermissionDenied):
        ListCommunityListings(Gate(), Repo()).execute(make_user(), query)
    assert calls == ["access"]
