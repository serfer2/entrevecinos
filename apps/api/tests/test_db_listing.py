import uuid
from decimal import Decimal

import pytest
from alembic import command
from sqlalchemy import Engine, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import (
    CategoryModel,
    CommunityModel,
    ListingImageModel,
    ListingModel,
    MediaAssetModel,
    UserModel,
)
from tests.conftest import alembic_config

pytestmark = pytest.mark.db

INITIAL_SLUGS = {
    "hogar-y-jardin",
    "electronica",
    "moda-y-complementos",
    "infantil",
    "deporte-y-ocio",
    "libros-y-musica",
    "motor",
    "servicios",
    "mascotas",
    "otros",
}


@pytest.fixture
def owner(db_session: Session) -> UserModel:
    user = UserModel(email="vecino@example.com", password_hash="hash", full_name="Alex Vecino")
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def community(db_session: Session, owner: UserModel) -> CommunityModel:
    community = CommunityModel(name="Los Olivos", created_by=owner.id)
    db_session.add(community)
    db_session.flush()
    return community


def make_listing(
    db_session: Session, owner: UserModel, community: CommunityModel, **overrides: object
) -> ListingModel:
    category = db_session.scalars(select(CategoryModel).where(CategoryModel.slug == "otros")).one()
    values = {
        "community_id": community.id,
        "owner_id": owner.id,
        "category_id": category.id,
        "title": "Bicicleta",
        "description": "Poco uso",
        "type": "sell",
        **overrides,
    }
    listing = ListingModel(**values)
    db_session.add(listing)
    db_session.flush()
    return listing


def make_asset(db_session: Session, owner: UserModel, key: str) -> MediaAssetModel:
    asset = MediaAssetModel(
        uploaded_by=owner.id, object_key=key, mime_type="image/jpeg", size_bytes=10
    )
    db_session.add(asset)
    db_session.flush()
    return asset


def test_initial_categories(db_session: Session) -> None:
    categories = db_session.scalars(select(CategoryModel)).all()

    assert {c.slug for c in categories} == INITIAL_SLUGS
    assert all(c.is_active for c in categories)


def test_listing_defaults_without_price(
    db_session: Session, owner: UserModel, community: CommunityModel
) -> None:
    listing = make_listing(db_session, owner, community)
    db_session.refresh(listing)

    assert listing.status == "active"
    assert listing.published_at is not None
    assert (listing.price, listing.currency, listing.deleted_at) == (None, None, None)


def test_listing_with_price_and_currency(
    db_session: Session, owner: UserModel, community: CommunityModel
) -> None:
    listing = make_listing(db_session, owner, community, price=Decimal("40.50"), currency="EUR")
    db_session.refresh(listing)

    assert (listing.price, listing.currency) == (Decimal("40.50"), "EUR")


@pytest.mark.parametrize(
    ("values", "constraint"),
    [
        ({"price": Decimal("-1"), "currency": "EUR"}, "ck_listing_price_not_negative"),
        ({"price": Decimal("10")}, "ck_listing_price_has_currency"),
        ({"currency": "EUR"}, "ck_listing_price_has_currency"),
        ({"price": Decimal("10"), "currency": "eur"}, "ck_listing_currency_format"),
        ({"title": "   "}, "ck_listing_title_not_blank"),
        ({"description": ""}, "ck_listing_description_not_blank"),
    ],
)
def test_listing_constraints(
    db_session: Session,
    owner: UserModel,
    community: CommunityModel,
    values: dict,
    constraint: str,
) -> None:
    with pytest.raises(IntegrityError, match=constraint):
        make_listing(db_session, owner, community, **values)


def test_only_one_cover_per_listing(
    db_session: Session, owner: UserModel, community: CommunityModel
) -> None:
    listing = make_listing(db_session, owner, community)
    first, second = make_asset(db_session, owner, "a"), make_asset(db_session, owner, "b")
    db_session.add(ListingImageModel(listing_id=listing.id, asset_id=first.id, is_cover=True))
    db_session.flush()
    db_session.add(
        ListingImageModel(listing_id=listing.id, asset_id=second.id, position=1, is_cover=True)
    )

    with pytest.raises(IntegrityError, match="uq_listing_image_listing_id_cover"):
        db_session.flush()


def test_positions_are_unique_per_listing(
    db_session: Session, owner: UserModel, community: CommunityModel
) -> None:
    listing = make_listing(db_session, owner, community)
    first, second = make_asset(db_session, owner, "a"), make_asset(db_session, owner, "b")
    db_session.add(ListingImageModel(listing_id=listing.id, asset_id=first.id, position=0))
    db_session.flush()
    db_session.add(ListingImageModel(listing_id=listing.id, asset_id=second.id, position=0))

    with pytest.raises(IntegrityError, match="ix_listing_image_listing_id_position"):
        db_session.flush()


def test_media_asset_rejects_other_mime_types(db_session: Session, owner: UserModel) -> None:
    db_session.add(
        MediaAssetModel(uploaded_by=owner.id, object_key="x", mime_type="image/gif", size_bytes=1)
    )

    with pytest.raises(IntegrityError, match="ck_media_asset_mime_type_allowed"):
        db_session.flush()


def test_avatar_references_media_asset(db_session: Session, owner: UserModel) -> None:
    owner.avatar_asset_id = make_asset(db_session, owner, "avatar").id
    db_session.flush()

    owner.avatar_asset_id = uuid.uuid4()
    with pytest.raises(IntegrityError, match="fk_users_avatar_asset_id_media_asset"):
        db_session.flush()


def test_migration_0004_is_reversible(db_engine: Engine) -> None:
    with db_engine.begin() as connection:
        command.downgrade(alembic_config(connection), "0003")
        assert not inspect(connection).has_table("listing")
        assert inspect(connection).has_table("community")

    with db_engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
        assert inspect(connection).has_table("listing_image")
