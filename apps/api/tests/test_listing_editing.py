import dataclasses
import uuid
from decimal import Decimal

import pytest

from entrevecinos.application.listings.editing import (
    EditableListing,
    ImageSelection,
    ListingChanges,
    ReplaceListingImages,
    UpdateListing,
    resolve_price,
)
from entrevecinos.application.unset import UNSET
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.listings.entities import ListingStatus
from entrevecinos.domain.listings.errors import (
    CurrencyWithoutPrice,
    InvalidCategory,
    InvalidImages,
    ListingLocked,
    ListingNotFound,
)
from tests.test_community_access import make_user
from tests.test_delete_listing import make_listing


def priced(price: str | None, currency: str | None):
    listing = make_listing(uuid.uuid4())
    return dataclasses.replace(listing, price=Decimal(price) if price else None, currency=currency)


@pytest.mark.parametrize(
    ("current", "price", "currency", "expected"),
    [
        (("10", "EUR"), UNSET, UNSET, {}),
        (("10", "EUR"), None, UNSET, {"price": None, "currency": None}),
        (("10", "USD"), Decimal("20"), UNSET, {"price": Decimal("20"), "currency": "USD"}),
        ((None, None), Decimal("20"), UNSET, {"price": Decimal("20"), "currency": "EUR"}),
        (("10", "EUR"), UNSET, "USD", {"price": Decimal("10"), "currency": "USD"}),
        (("10", "EUR"), Decimal("5"), None, {"price": Decimal("5"), "currency": "EUR"}),
    ],
)
def test_resolve_price(current, price, currency, expected) -> None:
    assert resolve_price(priced(*current), price, currency) == expected


@pytest.mark.parametrize(("price", "currency"), [(UNSET, "EUR"), (None, "EUR")])
def test_currency_without_resulting_price(price, currency) -> None:
    with pytest.raises(CurrencyWithoutPrice):
        resolve_price(priced(None, None), price, currency)


class Access:
    def __init__(self, member: bool = True) -> None:
        self.member = member

    def require_member(self, user, community_id):
        if not self.member:
            raise PermissionDenied


class Listings:
    def __init__(self, listing) -> None:
        self.listing = listing
        self.updated: dict | None = None
        self.images: list | None = None

    def get(self, listing_id):
        return self.listing if self.listing and self.listing.id == listing_id else None

    def update(self, listing_id, values):
        self.updated = dict(values)
        return self.listing

    def replace_images(self, listing_id, images):
        self.images = images
        return self.listing


class Categories:
    def __init__(self, active: bool = True) -> None:
        self.active = active

    def is_active(self, category_id):
        return self.active


class Media:
    def __init__(self, valid: bool = True) -> None:
        self.valid = valid
        self.calls: list = []

    def owned_available(self, asset_ids, user_id, listing_id=None):
        self.calls.append((asset_ids, listing_id))
        return self.valid


def test_editable_rules() -> None:
    author = make_user()
    listing = make_listing(author.id)

    assert EditableListing(Access(), Listings(listing)).require(author, listing.id) == listing
    with pytest.raises(ListingNotFound):
        EditableListing(Access(), Listings(None)).require(author, listing.id)
    with pytest.raises(PermissionDenied):
        EditableListing(Access(), Listings(listing)).require(make_user(), listing.id)
    with pytest.raises(PermissionDenied):
        EditableListing(Access(member=False), Listings(listing)).require(author, listing.id)
    hidden = dataclasses.replace(listing, status=ListingStatus.HIDDEN)
    with pytest.raises(ListingLocked) as error:
        EditableListing(Access(), Listings(hidden)).require(author, listing.id)
    assert "retirado" in error.value.detail


def test_update_only_sent_fields() -> None:
    author = make_user()
    listings = Listings(make_listing(author.id))
    use_case = UpdateListing(EditableListing(Access(), listings), Categories(), listings)

    use_case.execute(
        author, listings.listing.id, ListingChanges(title="Nuevo", price=Decimal("40"))
    )

    assert listings.updated == {"title": "Nuevo", "price": Decimal("40"), "currency": "EUR"}


def test_update_rejects_inactive_category() -> None:
    author = make_user()
    listings = Listings(make_listing(author.id))
    use_case = UpdateListing(EditableListing(Access(), listings), Categories(False), listings)

    with pytest.raises(InvalidCategory):
        use_case.execute(author, listings.listing.id, ListingChanges(category_id=uuid.uuid4()))
    assert listings.updated is None


def test_replace_images_order_and_cover() -> None:
    author = make_user()
    listings, media = Listings(make_listing(author.id)), Media()
    ids = [uuid.uuid4() for _ in range(3)]
    use_case = ReplaceListingImages(EditableListing(Access(), listings), media, listings)

    use_case.execute(
        author,
        listings.listing.id,
        [ImageSelection(ids[0]), ImageSelection(ids[1], True), ImageSelection(ids[2])],
    )

    assert [(i.asset_id, i.position, i.is_cover) for i in listings.images] == [
        (ids[0], 0, False),
        (ids[1], 1, True),
        (ids[2], 2, False),
    ]
    assert media.calls == [(ids, listings.listing.id)]

    use_case.execute(author, listings.listing.id, [ImageSelection(ids[2]), ImageSelection(ids[0])])
    assert [i.is_cover for i in listings.images] == [True, False]

    use_case.execute(author, listings.listing.id, [])
    assert listings.images == []


def test_replace_images_rejects_foreign_images() -> None:
    author = make_user()
    listings = Listings(make_listing(author.id))
    use_case = ReplaceListingImages(EditableListing(Access(), listings), Media(False), listings)

    with pytest.raises(InvalidImages):
        use_case.execute(author, listings.listing.id, [ImageSelection(uuid.uuid4())])
    assert listings.images is None
