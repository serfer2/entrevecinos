import uuid
from collections import defaultdict
from collections.abc import Iterable

from sqlalchemy import Select, func, select, update
from sqlalchemy.orm import Session

from entrevecinos.domain.listings.entities import (
    Listing,
    ListingImage,
    ListingOwner,
    ListingStatus,
    ListingType,
    NewListing,
)
from entrevecinos.infrastructure.db.models import ListingImageModel, ListingModel, UserModel


def listing_with_owner() -> Select[tuple[ListingModel, UserModel]]:
    """Consulta base de anuncios no eliminados con su autor (datos leídos de `users`).

    Toda lectura de anuncios parte de aquí: un anuncio eliminado no aparece en ninguna.
    """
    return (
        select(ListingModel, UserModel)
        .join(UserModel, UserModel.id == ListingModel.owner_id)
        .where(ListingModel.deleted_at.is_(None))
    )


class ListingLoader:
    """Convierte filas (anuncio, autor) en entidades cargando todas sus imágenes en una consulta."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def load(self, rows: Iterable[tuple[ListingModel, UserModel]]) -> list[Listing]:
        rows = list(rows)
        images: dict[uuid.UUID, list[ListingImage]] = defaultdict(list)
        if rows:
            for image in self._session.scalars(
                select(ListingImageModel)
                .where(ListingImageModel.listing_id.in_([listing.id for listing, _ in rows]))
                .order_by(ListingImageModel.listing_id, ListingImageModel.position)
            ):
                images[image.listing_id].append(
                    ListingImage(
                        asset_id=image.asset_id, position=image.position, is_cover=image.is_cover
                    )
                )
        return [self._to_domain(listing, owner, images[listing.id]) for listing, owner in rows]

    @staticmethod
    def _to_domain(model: ListingModel, owner: UserModel, images: list[ListingImage]) -> Listing:
        return Listing(
            id=model.id,
            community_id=model.community_id,
            owner=ListingOwner(
                id=owner.id, full_name=owner.full_name, phone=owner.phone, email=owner.email
            ),
            category_id=model.category_id,
            title=model.title,
            description=model.description,
            type=ListingType(model.type),
            price=model.price,
            currency=model.currency,
            status=ListingStatus(model.status),
            published_at=model.published_at,
            updated_at=model.updated_at,
            images=tuple(images),
            deleted_at=model.deleted_at,
        )


class SqlAlchemyListingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._loader = ListingLoader(session)

    def add(self, listing: NewListing) -> Listing:
        model = ListingModel(
            community_id=listing.community_id,
            owner_id=listing.owner_id,
            category_id=listing.category_id,
            title=listing.title,
            description=listing.description,
            type=listing.type,
            price=listing.price,
            currency=listing.currency,
            status=ListingStatus.ACTIVE,
        )
        self._session.add(model)
        self._session.flush()
        self._session.add_all(
            ListingImageModel(
                listing_id=model.id, asset_id=asset_id, position=position, is_cover=position == 0
            )
            for position, asset_id in enumerate(listing.image_asset_ids)
        )
        self._session.flush()
        found = self.get(model.id)
        assert found is not None
        return found

    def get(self, listing_id: uuid.UUID) -> Listing | None:
        self._session.expire_all()
        rows = self._session.execute(listing_with_owner().where(ListingModel.id == listing_id))
        found = self._loader.load(rows)
        return found[0] if found else None

    def soft_delete(self, listing_id: uuid.UUID) -> None:
        self._session.execute(
            update(ListingModel)
            .where(ListingModel.id == listing_id)
            .values(deleted_at=func.statement_timestamp(), status=ListingStatus.DELETED)
        )
