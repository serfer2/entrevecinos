import uuid

from entrevecinos.application.media.ports import MediaRepository, ObjectStorage
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.media.errors import MediaNotFound
from entrevecinos.domain.users.entities import PlatformRole, User


class GetImageUrl:
    def __init__(self, media: MediaRepository, storage: ObjectStorage, ttl_seconds: int) -> None:
        self._media = media
        self._storage = storage
        self._ttl_seconds = ttl_seconds

    def execute(self, user: User, asset_id: uuid.UUID) -> str:
        asset = self._media.get(asset_id)
        if asset is None:
            raise MediaNotFound
        readable = (
            asset.uploaded_by == user.id
            or user.platform_role is PlatformRole.PLATFORM_ADMIN
            or self._media.is_readable_by(asset_id, user.id)
        )
        if not readable:
            raise PermissionDenied
        return self._storage.presigned_get_url(asset.object_key, self._ttl_seconds)
