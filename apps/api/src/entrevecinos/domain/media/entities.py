import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ImageType(Enum):
    """Formatos de imagen admitidos: tipo MIME y extensión del objeto."""

    JPEG = ("image/jpeg", "jpg")
    PNG = ("image/png", "png")
    WEBP = ("image/webp", "webp")

    @property
    def mime_type(self) -> str:
        return self.value[0]

    @property
    def extension(self) -> str:
        return self.value[1]


def detect_image_type(header: bytes) -> ImageType | None:
    """Tipo real de la imagen según sus *magic bytes* (nunca según el nombre o el Content-Type)."""
    if header.startswith(b"\xff\xd8\xff"):
        return ImageType.JPEG
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return ImageType.PNG
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return ImageType.WEBP
    return None


@dataclass(frozen=True, slots=True)
class NewMediaAsset:
    uploaded_by: uuid.UUID
    object_key: str
    mime_type: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class MediaAsset:
    id: uuid.UUID
    uploaded_by: uuid.UUID
    object_key: str
    mime_type: str
    size_bytes: int
    created_at: datetime
