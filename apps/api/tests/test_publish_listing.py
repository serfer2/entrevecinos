import uuid
from decimal import Decimal

import pytest

from entrevecinos.application.listings.publish_listing import PublishListing, PublishListingCommand
from entrevecinos.domain.listings.entities import ListingType, normalize_price
from entrevecinos.domain.listings.errors import CurrencyWithoutPrice, InvalidCategory, InvalidImages


def test_normalize_price() -> None:
    assert normalize_price(None, None) == (None, None)
    assert normalize_price(Decimal("45"), None) == (Decimal("45"), "EUR")
    assert normalize_price(Decimal("45"), "USD") == (Decimal("45"), "USD")
    with pytest.raises(CurrencyWithoutPrice):
        normalize_price(None, "EUR")


class AllowAll:
    def require_member(self, user, community_id):
        return None


class Categories:
    def __init__(self, active: bool) -> None:
        self.active = active

    def is_active(self, category_id):
        return self.active


class Media:
    def __init__(self, valid: bool) -> None:
        self.valid = valid
        self.calls: list = []

    def owned_available(self, asset_ids, user_id, listing_id=None):
        self.calls.append(asset_ids)
        return self.valid


class Listings:
    def __init__(self) -> None:
        self.added = None

    def add(self, listing):
        self.added = listing
        return listing


class User:
    id = uuid.uuid4()


def command(**overrides) -> PublishListingCommand:
    values = {
        "category_id": uuid.uuid4(),
        "title": "Bicicleta",
        "description": "Poco uso",
        "type": ListingType.SELL,
    }
    return PublishListingCommand(**{**values, **overrides})


def test_publish_defaults_currency_to_eur() -> None:
    listings = Listings()
    use_case = PublishListing(AllowAll(), Categories(True), Media(True), listings)

    use_case.execute(User(), uuid.uuid4(), command(price=Decimal("45")))

    assert (listings.added.price, listings.added.currency) == (Decimal("45"), "EUR")


def test_publish_validates_category_and_images() -> None:
    images = (uuid.uuid4(), uuid.uuid4())
    with pytest.raises(InvalidCategory):
        PublishListing(AllowAll(), Categories(False), Media(True), Listings()).execute(
            User(), uuid.uuid4(), command()
        )
    with pytest.raises(InvalidImages):
        PublishListing(AllowAll(), Categories(True), Media(False), Listings()).execute(
            User(), uuid.uuid4(), command(image_asset_ids=images)
        )


def test_publish_without_images_skips_media_check() -> None:
    media = Media(False)
    listings = Listings()

    PublishListing(AllowAll(), Categories(True), media, listings).execute(
        User(), uuid.uuid4(), command()
    )

    assert media.calls == [] and listings.added.image_asset_ids == ()
