import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from entrevecinos.domain.listings.errors import CurrencyWithoutPrice

DEFAULT_CURRENCY = "EUR"
MAX_IMAGES = 10


class ListingType(StrEnum):
    SELL = "sell"
    WANTED = "wanted"
    OFFER_SERVICE = "offer_service"
    NEED_SERVICE = "need_service"
    FREE = "free"
    OTHER = "other"


class ListingStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    RESERVED = "reserved"
    COMPLETED = "completed"
    HIDDEN = "hidden"
    DELETED = "deleted"


@dataclass(frozen=True, slots=True)
class Category:
    id: uuid.UUID
    name: str
    slug: str
    is_active: bool


def normalize_price(
    price: Decimal | None, currency: str | None
) -> tuple[Decimal | None, str | None]:
    """Hay moneda si y solo si hay precio; sin moneda, el precio es en euros."""
    if price is None:
        if currency is not None:
            raise CurrencyWithoutPrice
        return None, None
    return price, currency or DEFAULT_CURRENCY


@dataclass(frozen=True, slots=True)
class ListingOwner:
    """Anunciante: datos leídos siempre de su perfil (no se copian en el anuncio)."""

    id: uuid.UUID
    full_name: str
    phone: str | None
    email: str


@dataclass(frozen=True, slots=True)
class ListingImage:
    asset_id: uuid.UUID
    position: int
    is_cover: bool


@dataclass(frozen=True, slots=True)
class NewListing:
    community_id: uuid.UUID
    owner_id: uuid.UUID
    category_id: uuid.UUID
    title: str
    description: str
    type: ListingType
    price: Decimal | None = None
    currency: str | None = None
    image_asset_ids: tuple[uuid.UUID, ...] = ()


@dataclass(frozen=True, slots=True)
class Listing:
    id: uuid.UUID
    community_id: uuid.UUID
    owner: ListingOwner
    category_id: uuid.UUID
    title: str
    description: str
    type: ListingType
    price: Decimal | None
    currency: str | None
    status: ListingStatus
    published_at: datetime
    updated_at: datetime
    images: tuple[ListingImage, ...] = field(default=())
    deleted_at: datetime | None = None
