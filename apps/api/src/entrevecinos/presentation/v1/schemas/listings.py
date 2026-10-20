import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    field_validator,
    model_validator,
)

from entrevecinos.domain.listings.entities import (
    MAX_IMAGES,
    Category,
    Listing,
    ListingStatus,
    ListingType,
)
from entrevecinos.presentation.v1.schemas.common import RequiredText
from entrevecinos.presentation.v1.schemas.media import media_url

# Decimal de extremo a extremo; en JSON, número (no cadena).
Price = Annotated[
    Decimal,
    Field(ge=0, le=Decimal("99999999.99"), max_digits=10, decimal_places=2),
    PlainSerializer(float, return_type=float, when_used="json"),
]
Currency = Annotated[str, Field(pattern=r"^[A-Z]{3}$")]


class CategoryResponse(BaseModel):
    """Esquema `Category` del contrato."""

    id: uuid.UUID
    name: str
    slug: str
    is_active: bool

    @classmethod
    def from_domain(cls, category: Category) -> Self:
        return cls(
            id=category.id, name=category.name, slug=category.slug, is_active=category.is_active
        )


class CategoriesResponse(BaseModel):
    items: list[CategoryResponse]


class ListingCreateRequest(BaseModel):
    """Esquema `ListingCreate` del contrato."""

    model_config = ConfigDict(extra="forbid")

    category_id: uuid.UUID
    title: RequiredText(160)
    description: RequiredText(5000)
    type: ListingType
    price: Price | None = None
    currency: Currency | None = None
    image_asset_ids: Annotated[list[uuid.UUID], Field(max_length=MAX_IMAGES)] = []

    @field_validator("currency")
    @classmethod
    def currency_requires_price(cls, value: str | None, info) -> str | None:
        if value is not None and info.data.get("price") is None:
            raise ValueError("currency requires a price")
        return value

    @field_validator("image_asset_ids")
    @classmethod
    def images_are_distinct(cls, value: list[uuid.UUID]) -> list[uuid.UUID]:
        if len(set(value)) != len(value):
            raise ValueError("image_asset_ids must be distinct")
        return value


class ListingUpdateRequest(BaseModel):
    """Esquema `ListingUpdate` del contrato (actualización parcial)."""

    model_config = ConfigDict(extra="forbid")

    # `None` solo como «no enviado» en los campos obligatorios: un `null` explícito → 422.
    category_id: uuid.UUID | None = None
    title: RequiredText(160) | None = None
    description: RequiredText(5000) | None = None
    type: ListingType | None = None
    price: Price | None = None
    currency: Currency | None = None

    @field_validator("category_id", "title", "description", "type", mode="before")
    @classmethod
    def not_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("cannot be null")
        return value

    @model_validator(mode="after")
    def at_least_one_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field is required")
        return self


class ListingStatusUpdateRequest(BaseModel):
    """Esquema `ListingStatusUpdate` del contrato."""

    model_config = ConfigDict(extra="forbid")

    status: Literal[
        ListingStatus.ACTIVE, ListingStatus.RESERVED, ListingStatus.COMPLETED, ListingStatus.HIDDEN
    ]


class ListingImageSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_id: uuid.UUID
    is_cover: bool = False


class ListingImagesUpdateRequest(BaseModel):
    """Esquema `ListingImagesUpdate` del contrato."""

    model_config = ConfigDict(extra="forbid")

    images: Annotated[list[ListingImageSelection], Field(max_length=MAX_IMAGES)]

    @field_validator("images")
    @classmethod
    def valid_selection(cls, value: list[ListingImageSelection]) -> list[ListingImageSelection]:
        if sum(image.is_cover for image in value) > 1:
            raise ValueError("At most one cover image")
        if len({image.asset_id for image in value}) != len(value):
            raise ValueError("asset_id must be distinct")
        return value


class ListingOwnerResponse(BaseModel):
    """Esquema `ListingOwner` del contrato: el canal de contacto del MVP (teléfono y correo).

    Solo forma parte de `Listing`, que solo se entrega a miembros aprobados de la comunidad.
    """

    id: uuid.UUID
    full_name: str
    phone: str | None
    email: str
    avatar_url: str | None = None


class ListingImageResponse(BaseModel):
    """Esquema `ListingImage` del contrato."""

    asset_id: uuid.UUID
    url: str
    position: int
    is_cover: bool


class ListingResponse(BaseModel):
    """Esquema `Listing` del contrato."""

    id: uuid.UUID
    community_id: uuid.UUID
    owner: ListingOwnerResponse
    category_id: uuid.UUID
    title: str
    description: str
    type: ListingType
    price: Price | None
    currency: str | None
    images: list[ListingImageResponse]
    status: ListingStatus
    published_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, listing: Listing) -> Self:
        return cls(
            id=listing.id,
            community_id=listing.community_id,
            owner=ListingOwnerResponse(
                id=listing.owner.id,
                full_name=listing.owner.full_name,
                phone=listing.owner.phone,
                email=listing.owner.email,
            ),
            category_id=listing.category_id,
            title=listing.title,
            description=listing.description,
            type=listing.type,
            price=listing.price,
            currency=listing.currency,
            images=[
                ListingImageResponse(
                    asset_id=image.asset_id,
                    url=media_url(image.asset_id),
                    position=image.position,
                    is_cover=image.is_cover,
                )
                for image in listing.images
            ],
            status=listing.status,
            published_at=listing.published_at,
            updated_at=listing.updated_at,
        )
