from entrevecinos.domain.errors import NotFoundError, PermissionDenied


class ListingNotFound(NotFoundError):
    """El anuncio no existe, está eliminado o el usuario no puede verlo."""


class InvalidCategory(Exception):
    """La categoría no existe o no está activa."""


class InvalidImages(Exception):
    """Alguna imagen no existe, no es del usuario o ya está asociada a otro anuncio."""


class CurrencyWithoutPrice(Exception):
    """Se indicó una moneda sin precio."""


class ListingStatusConflict(Exception):
    """El cambio de estado no es una transición permitida desde el estado actual (409)."""

    SAME = "El anuncio ya está en ese estado."
    NOT_ALLOWED = "Transición de estado no permitida."
    COMPLETED_FINAL = "Un anuncio finalizado no puede cambiar de estado."

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class ListingLocked(PermissionDenied):
    """El autor no puede modificar el anuncio en su estado actual (retirado, finalizado…)."""

    RETIRED = "Este anuncio ha sido retirado por la administración de la comunidad."
    COMPLETED = "Este anuncio está finalizado y no se puede editar."

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail
