import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from entrevecinos.application.pagination import PageRequest, PageResult
from entrevecinos.domain.listings.entities import (
    Category,
    Listing,
    ListingImage,
    ListingSort,
    ListingStatus,
    ListingType,
    NewListing,
    SortOrder,
)


@dataclass(frozen=True, slots=True)
class ListingQuery:
    """Criterios del listado de una comunidad (búsqueda, filtros y orden)."""

    community_id: uuid.UUID
    page: PageRequest
    text: str | None = None
    type: ListingType | None = None
    category_id: uuid.UUID | None = None
    sort: ListingSort = ListingSort.PUBLISHED_AT
    order: SortOrder = SortOrder.DESC


class CategoryRepository(Protocol):
    def list_active(self) -> list[Category]:
        """Categorías activas, ordenadas por nombre y con «Otros» al final."""
        ...

    def is_active(self, category_id: uuid.UUID) -> bool: ...


class ListingRepository(Protocol):
    def add(self, listing: NewListing) -> Listing:
        """Guarda el anuncio y sus imágenes (en orden; la primera es la portada)."""
        ...

    def get(self, listing_id: uuid.UUID) -> Listing | None:
        """Anuncio no eliminado, con su autor y sus imágenes."""
        ...

    def search(self, query: ListingQuery) -> PageResult[Listing]:
        """Anuncios visibles en la comunidad que cumplen `query`."""
        ...

    def update(self, listing_id: uuid.UUID, values: Mapping[str, object]) -> Listing:
        """Actualiza solo los campos de `values` y devuelve el anuncio actualizado."""
        ...

    def replace_images(self, listing_id: uuid.UUID, images: list[ListingImage]) -> Listing:
        """Sustituye el conjunto de imágenes en la misma transacción."""
        ...

    def set_status(
        self, listing_id: uuid.UUID, status: ListingStatus, moderator_id: uuid.UUID | None
    ) -> Listing:
        """Cambia el estado. Al retirar (`hidden`) registra quién y cuándo; si no, lo vacía."""
        ...

    def soft_delete(self, listing_id: uuid.UUID) -> None:
        """Marca el anuncio como eliminado (`deleted_at`, `status = deleted`)."""
        ...
