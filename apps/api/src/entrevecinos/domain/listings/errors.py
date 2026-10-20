from entrevecinos.domain.errors import NotFoundError


class ListingNotFound(NotFoundError):
    """El anuncio no existe, está eliminado o el usuario no puede verlo."""


class InvalidCategory(Exception):
    """La categoría no existe o no está activa."""


class InvalidImages(Exception):
    """Alguna imagen no existe, no es del usuario o ya está asociada a otro anuncio."""


class CurrencyWithoutPrice(Exception):
    """Se indicó una moneda sin precio."""
