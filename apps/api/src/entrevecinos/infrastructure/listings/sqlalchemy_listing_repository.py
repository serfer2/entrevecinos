import uuid
from collections import defaultdict
from collections.abc import Iterable, Mapping

from sqlalchemy import ColumnElement, Select, delete, false, func, select, update
from sqlalchemy.orm import Session

from entrevecinos.application.listings.ports import ListingQuery
from entrevecinos.application.pagination import PageResult
from entrevecinos.domain.listings.entities import (
    LISTED_STATUSES,
    Listing,
    ListingImage,
    ListingOwner,
    ListingStatus,
    ListingType,
    NewListing,
)
from entrevecinos.domain.listings.search import prefix_tsquery
from entrevecinos.infrastructure.db.models import ListingImageModel, ListingModel, UserModel
from entrevecinos.infrastructure.db.models.listing import SEARCH_CONFIG


def listing_with_owner() -> Select[tuple[ListingModel, UserModel]]:
    """Consulta base de anuncios no eliminados con su autor (datos leídos de `users`).

    Toda lectura de anuncios parte de aquí: un anuncio eliminado no aparece en ninguna.
    """
    return (
        select(ListingModel, UserModel)
        .join(UserModel, UserModel.id == ListingModel.owner_id)
        # Los anuncios de cuentas eliminadas tampoco se muestran (contrato, `users_me.yaml`).
        .where(ListingModel.deleted_at.is_(None), UserModel.deleted_at.is_(None))
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

    def search(self, query: ListingQuery) -> PageResult[Listing]:
        # Misma consulta base para la página y el total (visibilidad y criterios de búsqueda).
        visible = listing_with_owner().where(
            *self._visible_in_community(query), *self._criteria(query)
        )
        total = self._session.scalar(select(func.count()).select_from(visible.subquery()))
        rows = self._session.execute(
            visible.order_by(ListingModel.published_at.desc(), ListingModel.id.desc())
            .offset(query.page.offset)
            .limit(query.page.page_size)
        )
        return PageResult(items=self._loader.load(rows), total=total or 0)

    @staticmethod
    def _visible_in_community(query: ListingQuery) -> list[ColumnElement[bool]]:
        """Filtro común del listado y de su `total`: lo que un miembro ve en la comunidad."""
        conditions = [
            ListingModel.community_id == query.community_id,
            ListingModel.status.in_(LISTED_STATUSES),
            ListingModel.deleted_at.is_(None),
        ]
        return conditions

    @staticmethod
    def _criteria(query: ListingQuery) -> list[ColumnElement[bool]]:
        """Búsqueda y filtros elegidos por el usuario, combinados con AND."""
        conditions: list[ColumnElement[bool]] = []
        if query.text is not None:
            tsquery = prefix_tsquery(query.text)
            # Sin palabras válidas (p. ej. «a b»), no hay coincidencias.
            conditions.append(
                ListingModel.search_vector.bool_op("@@")(func.to_tsquery(SEARCH_CONFIG, tsquery))
                if tsquery
                else false()
            )
        if query.type is not None:
            conditions.append(ListingModel.type == query.type)
        # Una categoría inexistente o inactiva simplemente no tiene anuncios: lista vacía.
        if query.category_id is not None:
            conditions.append(ListingModel.category_id == query.category_id)
        return conditions

    def update(self, listing_id: uuid.UUID, values: Mapping[str, object]) -> Listing:
        model = self._session.get_one(ListingModel, listing_id)
        for field, value in values.items():
            setattr(model, field, value)
        self._session.flush()
        found = self.get(listing_id)
        assert found is not None
        return found

    def replace_images(self, listing_id: uuid.UUID, images: list[ListingImage]) -> Listing:
        self._session.execute(
            delete(ListingImageModel).where(ListingImageModel.listing_id == listing_id)
        )
        self._session.add_all(
            ListingImageModel(
                listing_id=listing_id,
                asset_id=image.asset_id,
                position=image.position,
                is_cover=image.is_cover,
            )
            for image in images
        )
        # La edición de las imágenes cuenta como actualización del anuncio.
        self._session.execute(
            update(ListingModel)
            .where(ListingModel.id == listing_id)
            .values(updated_at=func.statement_timestamp())
        )
        self._session.flush()
        found = self.get(listing_id)
        assert found is not None
        return found

    def soft_delete(self, listing_id: uuid.UUID) -> None:
        self._session.execute(
            update(ListingModel)
            .where(ListingModel.id == listing_id)
            .values(deleted_at=func.statement_timestamp(), status=ListingStatus.DELETED)
        )
