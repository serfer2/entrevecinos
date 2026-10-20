import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    BigInteger,
    Boolean,
    CheckConstraint,
    Computed,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from entrevecinos.infrastructure.db.base import Base

# Configuración de búsqueda en español sin tildes (migración 0005).
SEARCH_CONFIG = "es_unaccent"
SEARCH_VECTOR = (
    f"setweight(to_tsvector('{SEARCH_CONFIG}', coalesce(title, '')), 'A') || "
    f"setweight(to_tsvector('{SEARCH_CONFIG}', coalesce(description, '')), 'B')"
)

LISTING_TYPE = Enum(
    "sell", "wanted", "offer_service", "need_service", "free", "other", name="listing_type"
)
LISTING_STATUS = Enum(
    "draft", "active", "reserved", "completed", "hidden", "deleted", name="listing_status"
)
IMAGE_MIME_TYPES = ("image/jpeg", "image/png", "image/webp")


class CategoryModel(Base):
    __tablename__ = "category"
    __table_args__ = (CheckConstraint("slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name="slug_format"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(80), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))


class ListingModel(Base):
    __tablename__ = "listing"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="title_not_blank"),
        CheckConstraint("length(trim(description)) > 0", name="description_not_blank"),
        CheckConstraint("price IS NULL OR price >= 0", name="price_not_negative"),
        CheckConstraint("currency ~ '^[A-Z]{3}$'", name="currency_format"),
        # Hay moneda si y solo si hay precio.
        CheckConstraint("(price IS NULL) = (currency IS NULL)", name="price_has_currency"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    community_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("community.id", ondelete="RESTRICT"))
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("category.id", ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(LISTING_TYPE)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    currency: Mapped[str | None] = mapped_column(CHAR(3))
    status: Mapped[str] = mapped_column(LISTING_STATUS, server_default="active")
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.statement_timestamp()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Retirada por moderación: quién y cuándo (se vacían al restaurar).
    hidden_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    hidden_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Columna generada por PostgreSQL: el ORM nunca la escribe.
    search_vector: Mapped[str] = mapped_column(
        TSVECTOR, Computed(SEARCH_VECTOR, persisted=True), deferred=True
    )


# Índices del modelo de datos (nombres explícitos: la convención no admite expresiones DESC).
Index(
    "ix_listing_community_id_status_published_at",
    ListingModel.community_id,
    ListingModel.status,
    ListingModel.published_at.desc(),
)
Index(
    "ix_listing_community_id_type_published_at",
    ListingModel.community_id,
    ListingModel.type,
    ListingModel.published_at.desc(),
)
Index(
    "ix_listing_category_id_published_at",
    ListingModel.category_id,
    ListingModel.published_at.desc(),
)
Index("ix_listing_price", ListingModel.price)
Index("ix_listing_search_vector", ListingModel.search_vector, postgresql_using="gin")
Index("ix_listing_owner_id", ListingModel.owner_id)


class MediaAssetModel(Base):
    __tablename__ = "media_asset"
    __table_args__ = (
        CheckConstraint(
            "mime_type IN ('image/jpeg', 'image/png', 'image/webp')", name="mime_type_allowed"
        ),
        CheckConstraint("size_bytes > 0", name="size_positive"),
        Index(None, "uploaded_by"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    object_key: Mapped[str] = mapped_column(String(512), unique=True)
    mime_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    sha256: Mapped[str | None] = mapped_column(CHAR(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ListingImageModel(Base):
    __tablename__ = "listing_image"
    __table_args__ = (
        CheckConstraint("position >= 0", name="position_not_negative"),
        Index(None, "asset_id"),
        Index(None, "listing_id", "position", unique=True),
        # Como máximo una portada por anuncio.
        Index(
            "uq_listing_image_listing_id_cover",
            "listing_id",
            unique=True,
            postgresql_where=text("is_cover"),
        ),
    )

    listing_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("listing.id", ondelete="CASCADE"), primary_key=True
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("media_asset.id", ondelete="RESTRICT"), primary_key=True
    )
    position: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))
    is_cover: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
