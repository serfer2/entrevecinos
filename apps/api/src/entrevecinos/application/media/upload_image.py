import hashlib
import logging
import uuid

from entrevecinos.application.media.ports import MediaRepository, ObjectStorage
from entrevecinos.domain.media.entities import MediaAsset, NewMediaAsset, detect_image_type
from entrevecinos.domain.media.errors import EmptyImage, ImageTooLarge, UnsupportedImageType

logger = logging.getLogger(__name__)


class UploadImage:
    def __init__(self, media: MediaRepository, storage: ObjectStorage, max_bytes: int) -> None:
        self._media = media
        self._storage = storage
        self._max_bytes = max_bytes

    def execute(self, uploader_id: uuid.UUID, data: bytes) -> MediaAsset:
        if not data:
            raise EmptyImage
        if len(data) > self._max_bytes:
            raise ImageTooLarge(self._max_bytes)
        image_type = detect_image_type(data[:16])
        if image_type is None:
            raise UnsupportedImageType

        # Nunca el nombre original: solo el usuario y un identificador aleatorio.
        key = f"media/{uploader_id}/{uuid.uuid4()}.{image_type.extension}"
        self._storage.put(key, data, image_type.mime_type)
        try:
            return self._media.add(
                NewMediaAsset(
                    uploaded_by=uploader_id,
                    object_key=key,
                    mime_type=image_type.mime_type,
                    size_bytes=len(data),
                    sha256=hashlib.sha256(data).hexdigest(),
                )
            )
        except Exception:
            logger.exception("Imagen subida pero no registrada (objeto huérfano): %s", key)
            raise
