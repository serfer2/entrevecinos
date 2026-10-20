from entrevecinos.domain.errors import NotFoundError, PermissionDenied


class ListingNotFound(NotFoundError):
    """El anuncio no existe, está eliminado o el usuario no puede verlo."""


class InvalidCategory(Exception):
    """La categoría no existe o no está activa."""


class InvalidImages(Exception):
    """Alguna imagen no existe, no es del usuario o ya está asociada a otro anuncio."""


class CurrencyWithoutPrice(Exception):
    """Se indicó una moneda sin precio."""


class ListingLocked(PermissionDenied):
    """El autor no puede modificar el anuncio en su estado actual (retirado, finalizado…)."""

    RETIRED = "Este anuncio ha sido retirado por la administración de la comunidad."

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail
