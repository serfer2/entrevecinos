import uuid
from typing import Protocol

from entrevecinos.domain.media.entities import MediaAsset, NewMediaAsset


class ObjectStorage(Protocol):
    def put(self, key: str, data: bytes, content_type: str) -> None: ...

    def presigned_get_url(self, key: str, expires_in: int) -> str:
        """URL temporal de lectura para el navegador (no hace llamadas de red)."""
        ...


class MediaRepository(Protocol):
    def add(self, asset: NewMediaAsset) -> MediaAsset: ...

    def get(self, asset_id: uuid.UUID) -> MediaAsset | None: ...

    def owned_unattached(self, asset_ids: list[uuid.UUID], user_id: uuid.UUID) -> bool:
        """Si todas las imágenes existen, las subió `user_id` y no están en ningún anuncio."""
        ...

    def is_readable_by(self, asset_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Si la imagen está en algún anuncio no eliminado que el usuario puede ver."""
        ...
