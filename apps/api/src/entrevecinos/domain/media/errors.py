from entrevecinos.domain.errors import NotFoundError


class MediaNotFound(NotFoundError):
    """La imagen no existe."""


class EmptyImage(Exception):
    """El fichero enviado está vacío."""


class ImageTooLarge(Exception):
    def __init__(self, max_bytes: int) -> None:
        super().__init__(f"Image larger than {max_bytes} bytes")
        self.max_bytes = max_bytes


class UnsupportedImageType(Exception):
    """El contenido no es JPEG, PNG ni WebP."""
