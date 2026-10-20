import uuid
from datetime import datetime

from pydantic import BaseModel

from entrevecinos.domain.media.entities import MediaAsset


def media_url(asset_id: uuid.UUID) -> str:
    """URL relativa de lectura de una imagen (`GET /v1/media/{id}`)."""
    return f"/v1/media/{asset_id}"


class MediaAssetResponse(BaseModel):
    """Esquema `MediaAsset` del contrato."""

    id: uuid.UUID
    url: str
    mime_type: str
    size_bytes: int
    created_at: datetime

    @classmethod
    def from_domain(cls, asset: MediaAsset) -> "MediaAssetResponse":
        return cls(
            id=asset.id,
            url=media_url(asset.id),
            mime_type=asset.mime_type,
            size_bytes=asset.size_bytes,
            created_at=asset.created_at,
        )
