"""Crea categorías (con datos iniciales), anuncios, ficheros de imagen e imágenes de anuncio.

Añade también la FK users.avatar_asset_id → media_asset.id, pendiente desde 0001.

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

listing_type = sa.Enum(
    "sell", "wanted", "offer_service", "need_service", "free", "other", name="listing_type"
)
listing_status = sa.Enum(
    "draft", "active", "reserved", "completed", "hidden", "deleted", name="listing_status"
)

INITIAL_CATEGORIES = [
    ("Hogar y jardín", "hogar-y-jardin"),
    ("Electrónica", "electronica"),
    ("Moda y complementos", "moda-y-complementos"),
    ("Infantil", "infantil"),
    ("Deporte y ocio", "deporte-y-ocio"),
    ("Libros y música", "libros-y-musica"),
    ("Motor", "motor"),
    ("Servicios", "servicios"),
    ("Mascotas", "mascotas"),
    ("Otros", "otros"),
]


def upgrade() -> None:
    category = op.create_table(
        "category",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name=op.f("ck_category_slug_format")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_category")),
        sa.UniqueConstraint("name", name=op.f("uq_category_name")),
        sa.UniqueConstraint("slug", name=op.f("uq_category_slug")),
    )
    op.bulk_insert(category, [{"name": n, "slug": s} for n, s in INITIAL_CATEGORIES])

    op.create_table(
        "listing",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("community_id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("type", listing_type, nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.CHAR(3), nullable=True),
        sa.Column("status", listing_status, server_default="active", nullable=False),
        sa.Column(
            "published_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("length(trim(title)) > 0", name=op.f("ck_listing_title_not_blank")),
        sa.CheckConstraint(
            "length(trim(description)) > 0", name=op.f("ck_listing_description_not_blank")
        ),
        sa.CheckConstraint(
            "price IS NULL OR price >= 0", name=op.f("ck_listing_price_not_negative")
        ),
        sa.CheckConstraint("currency ~ '^[A-Z]{3}$'", name=op.f("ck_listing_currency_format")),
        sa.CheckConstraint(
            "(price IS NULL) = (currency IS NULL)", name=op.f("ck_listing_price_has_currency")
        ),
        sa.ForeignKeyConstraint(
            ["community_id"],
            ["community.id"],
            name=op.f("fk_listing_community_id_community"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"], name=op.f("fk_listing_owner_id_users"), ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["category.id"],
            name=op.f("fk_listing_category_id_category"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_listing")),
    )
    op.create_index(
        "ix_listing_community_id_status_published_at",
        "listing",
        ["community_id", "status", sa.text("published_at DESC")],
    )
    op.create_index(
        "ix_listing_community_id_type_published_at",
        "listing",
        ["community_id", "type", sa.text("published_at DESC")],
    )
    op.create_index(
        "ix_listing_category_id_published_at",
        "listing",
        ["category_id", sa.text("published_at DESC")],
    )
    op.create_index("ix_listing_price", "listing", ["price"])
    op.create_index("ix_listing_owner_id", "listing", ["owner_id"])

    op.create_table(
        "media_asset",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("uploaded_by", sa.Uuid(), nullable=False),
        sa.Column("object_key", sa.String(512), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.CHAR(64), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "mime_type IN ('image/jpeg', 'image/png', 'image/webp')",
            name=op.f("ck_media_asset_mime_type_allowed"),
        ),
        sa.CheckConstraint("size_bytes > 0", name=op.f("ck_media_asset_size_positive")),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            name=op.f("fk_media_asset_uploaded_by_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_media_asset")),
        sa.UniqueConstraint("object_key", name=op.f("uq_media_asset_object_key")),
    )
    op.create_index(op.f("ix_media_asset_uploaded_by"), "media_asset", ["uploaded_by"])

    op.create_table(
        "listing_image",
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("asset_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.SmallInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_cover", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.CheckConstraint("position >= 0", name=op.f("ck_listing_image_position_not_negative")),
        sa.ForeignKeyConstraint(
            ["listing_id"],
            ["listing.id"],
            name=op.f("fk_listing_image_listing_id_listing"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["asset_id"],
            ["media_asset.id"],
            name=op.f("fk_listing_image_asset_id_media_asset"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("listing_id", "asset_id", name=op.f("pk_listing_image")),
    )
    op.create_index(op.f("ix_listing_image_asset_id"), "listing_image", ["asset_id"])
    op.create_index(
        op.f("ix_listing_image_listing_id_position"),
        "listing_image",
        ["listing_id", "position"],
        unique=True,
    )
    op.create_index(
        "uq_listing_image_listing_id_cover",
        "listing_image",
        ["listing_id"],
        unique=True,
        postgresql_where=sa.text("is_cover"),
    )

    op.create_foreign_key(
        op.f("fk_users_avatar_asset_id_media_asset"),
        "users",
        "media_asset",
        ["avatar_asset_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("fk_users_avatar_asset_id_media_asset"), "users", type_="foreignkey")
    op.drop_table("listing_image")
    op.drop_table("media_asset")
    op.drop_table("listing")
    op.drop_table("category")
    listing_status.drop(op.get_bind(), checkfirst=True)
    listing_type.drop(op.get_bind(), checkfirst=True)
