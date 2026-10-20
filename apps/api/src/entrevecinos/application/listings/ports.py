import uuid
from dataclasses import dataclass
from typing import Protocol

from entrevecinos.application.pagination import PageRequest, PageResult
from entrevecinos.domain.listings.entities import (
    Category,
    Listing,
    ListingSort,
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

    def soft_delete(self, listing_id: uuid.UUID) -> None:
        """Marca el anuncio como eliminado (`deleted_at`, `status = deleted`)."""
        ...
