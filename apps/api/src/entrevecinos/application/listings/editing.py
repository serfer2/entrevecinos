import uuid
from dataclasses import dataclass
from decimal import Decimal

from entrevecinos.application.authorization.community_access import CommunityAccess
from entrevecinos.application.listings.ports import CategoryRepository, ListingRepository
from entrevecinos.application.media.ports import MediaRepository
from entrevecinos.application.unset import UNSET, Unset
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.listings.entities import (
    DEFAULT_CURRENCY,
    Listing,
    ListingImage,
    ListingStatus,
    ListingType,
)
from entrevecinos.domain.listings.errors import (
    CurrencyWithoutPrice,
    InvalidCategory,
    InvalidImages,
    ListingLocked,
    ListingNotFound,
)
from entrevecinos.domain.users.entities import User


class EditableListing:
    """Regla común de edición: solo el autor, todavía miembro aprobado, y anuncio no retirado ni
    finalizado."""

    def __init__(self, access: CommunityAccess, listings: ListingRepository) -> None:
        self._access = access
        self._listings = listings

    def require(self, user: User, listing_id: uuid.UUID) -> Listing:
        listing = self._listings.get(listing_id)
        if listing is None:
            raise ListingNotFound
        if listing.owner.id != user.id:
            raise PermissionDenied
        # Un autor expulsado o bloqueado ya no puede editar sus anuncios.
        self._access.require_member(user, listing.community_id)
        if listing.status is ListingStatus.HIDDEN:
            raise ListingLocked(ListingLocked.RETIRED)
        if listing.status is ListingStatus.COMPLETED:
            raise ListingLocked(ListingLocked.COMPLETED)
        return listing


@dataclass(frozen=True, slots=True)
class ListingChanges:
    category_id: uuid.UUID | Unset = UNSET
    title: str | Unset = UNSET
    description: str | Unset = UNSET
    type: ListingType | Unset = UNSET
    price: Decimal | None | Unset = UNSET
    currency: str | None | Unset = UNSET


def resolve_price(
    current: Listing, price: Decimal | None | Unset, currency: str | None | Unset
) -> dict[str, object]:
    """Precio y moneda resultantes, coherentes: moneda si y solo si hay precio."""
    if price is UNSET and currency is UNSET:
        return {}
    new_price = current.price if price is UNSET else price
    if currency is not UNSET:
        new_currency = currency
    elif new_price is None:
        new_currency = None
    else:
        new_currency = current.currency or DEFAULT_CURRENCY
    if new_price is None and new_currency is not None:
        raise CurrencyWithoutPrice
    if new_price is not None and new_currency is None:
        new_currency = DEFAULT_CURRENCY
    return {"price": new_price, "currency": new_currency}


class UpdateListing:
    def __init__(
        self,
        editable: EditableListing,
        categories: CategoryRepository,
        listings: ListingRepository,
    ) -> None:
        self._editable = editable
        self._categories = categories
        self._listings = listings

    def execute(self, user: User, listing_id: uuid.UUID, changes: ListingChanges) -> Listing:
        current = self._editable.require(user, listing_id)
        if changes.category_id is not UNSET and not self._categories.is_active(changes.category_id):
            raise InvalidCategory
        values: dict[str, object] = {
            field: value
            for field, value in {
                "category_id": changes.category_id,
                "title": changes.title,
                "description": changes.description,
                "type": changes.type,
            }.items()
            if value is not UNSET
        }
        values.update(resolve_price(current, changes.price, changes.currency))
        return self._listings.update(listing_id, values)


@dataclass(frozen=True, slots=True)
class ImageSelection:
    asset_id: uuid.UUID
    is_cover: bool = False


class ReplaceListingImages:
    def __init__(
        self, editable: EditableListing, media: MediaRepository, listings: ListingRepository
    ) -> None:
        self._editable = editable
        self._media = media
        self._listings = listings

    def execute(self, user: User, listing_id: uuid.UUID, images: list[ImageSelection]) -> Listing:
        self._editable.require(user, listing_id)
        ids = [image.asset_id for image in images]
        if ids and not self._media.owned_available(ids, user.id, listing_id):
            raise InvalidImages
        cover = next((i for i, image in enumerate(images) if image.is_cover), 0)
        return self._listings.replace_images(
            listing_id,
            [
                ListingImage(asset_id=image.asset_id, position=index, is_cover=index == cover)
                for index, image in enumerate(images)
            ],
        )
