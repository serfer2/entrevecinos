import uuid

from entrevecinos.application.listings.ports import ListingRepository
from entrevecinos.application.listings.visibility import ListingVisibility
from entrevecinos.application.media.ports import MediaRepository, ObjectStorage
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.media.errors import MediaNotFound
from entrevecinos.domain.users.entities import User


class GetImageUrl:
    """URL prefirmada de una imagen: la ve quien la subió o quien puede ver su anuncio."""

    def __init__(
        self,
        media: MediaRepository,
        storage: ObjectStorage,
        ttl_seconds: int,
        listings: ListingRepository,
        visibility: ListingVisibility,
    ) -> None:
        self._media = media
        self._storage = storage
        self._ttl_seconds = ttl_seconds
        self._listings = listings
        self._visibility = visibility

    def execute(self, user: User, asset_id: uuid.UUID) -> str:
        asset = self._media.get(asset_id)
        if asset is None:
            raise MediaNotFound
        if asset.uploaded_by != user.id and not self._can_view_listing(user, asset_id):
            raise PermissionDenied
        return self._storage.presigned_get_url(asset.object_key, self._ttl_seconds)

    def _can_view_listing(self, user: User, asset_id: uuid.UUID) -> bool:
        listing_id = self._media.listing_using(asset_id)
        listing = self._listings.get(listing_id) if listing_id else None
        return listing is not None and self._visibility.can_view(user, listing)
