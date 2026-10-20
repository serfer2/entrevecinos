import uuid
from typing import Protocol

from entrevecinos.domain.listings.entities import Category, Listing, NewListing


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
