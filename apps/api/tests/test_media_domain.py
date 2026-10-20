import uuid

import pytest

from entrevecinos.application.media.get_image_url import GetImageUrl
from entrevecinos.application.media.upload_image import UploadImage
from entrevecinos.domain.errors import PermissionDenied
from entrevecinos.domain.media.entities import (
    ImageType,
    MediaAsset,
    NewMediaAsset,
    detect_image_type,
)
from entrevecinos.domain.media.errors import (
    EmptyImage,
    ImageTooLarge,
    MediaNotFound,
    UnsupportedImageType,
)
from tests.fakes import InMemoryObjectStorage
from tests.images import GIF, JPEG, PDF, PNG, WEBP
from tests.test_community_access import make_user


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (JPEG, ImageType.JPEG),
        (PNG, ImageType.PNG),
        (WEBP, ImageType.WEBP),
        (PDF, None),
        (GIF, None),
        (b"\xff\xd8", None),
        (b"RIFF\x00\x00\x00\x00WAVE", None),
        (b"", None),
    ],
)
def test_detect_image_type(data: bytes, expected: ImageType | None) -> None:
    assert detect_image_type(data) is expected


class FakeMediaRepository:
    def __init__(self) -> None:
        self.assets: dict[uuid.UUID, MediaAsset] = {}
        self.listing_of: dict[uuid.UUID, uuid.UUID] = {}

    def add(self, asset: NewMediaAsset) -> MediaAsset:
        from datetime import UTC, datetime

        stored = MediaAsset(
            id=uuid.uuid4(),
            uploaded_by=asset.uploaded_by,
            object_key=asset.object_key,
            mime_type=asset.mime_type,
            size_bytes=asset.size_bytes,
            created_at=datetime.now(UTC),
        )
        self.assets[stored.id] = stored
        return stored

    def get(self, asset_id: uuid.UUID) -> MediaAsset | None:
        return self.assets.get(asset_id)

    def listing_using(self, asset_id: uuid.UUID) -> uuid.UUID | None:
        return self.listing_of.get(asset_id)


def test_upload_stores_object_with_random_key() -> None:
    media, storage, uploader = FakeMediaRepository(), InMemoryObjectStorage(), uuid.uuid4()

    asset = UploadImage(media, storage, max_bytes=1000).execute(uploader, PNG)

    assert asset.mime_type == "image/png"
    assert asset.size_bytes == len(PNG)
    assert asset.object_key.startswith(f"media/{uploader}/") and asset.object_key.endswith(".png")
    assert storage.objects[asset.object_key] == (PNG, "image/png")


@pytest.mark.parametrize(
    ("data", "error"),
    [(b"", EmptyImage), (JPEG + b"\x00" * 1000, ImageTooLarge), (PDF, UnsupportedImageType)],
)
def test_upload_rejects_invalid_files(data: bytes, error: type[Exception]) -> None:
    media, storage = FakeMediaRepository(), InMemoryObjectStorage()

    with pytest.raises(error):
        UploadImage(media, storage, max_bytes=1000).execute(uuid.uuid4(), data)
    assert storage.objects == {} and media.assets == {}


class Listings:
    def __init__(self, listing) -> None:
        self.listing = listing

    def get(self, listing_id):
        return self.listing if self.listing and self.listing.id == listing_id else None


class Visibility:
    def __init__(self, viewers) -> None:
        self.viewers = viewers

    def can_view(self, user, listing):
        return user.id in self.viewers


def test_image_url_permissions() -> None:
    from tests.test_delete_listing import make_listing

    media, storage = FakeMediaRepository(), InMemoryObjectStorage()
    owner, member, outsider = make_user(), make_user(), make_user()
    asset = UploadImage(media, storage, max_bytes=1000).execute(owner.id, JPEG)
    listing = make_listing(owner.id)
    media.listing_of[asset.id] = listing.id
    get_url = GetImageUrl(media, storage, 300, Listings(listing), Visibility({member.id}))

    assert "X-Amz-Expires=300" in get_url.execute(owner, asset.id)
    assert get_url.execute(member, asset.id).startswith("http://localhost:9000/")
    with pytest.raises(PermissionDenied):
        get_url.execute(outsider, asset.id)
    with pytest.raises(MediaNotFound):
        get_url.execute(owner, uuid.uuid4())


def test_unattached_image_is_only_for_its_uploader() -> None:
    media, storage = FakeMediaRepository(), InMemoryObjectStorage()
    owner, other = make_user(), make_user()
    asset = UploadImage(media, storage, max_bytes=1000).execute(owner.id, JPEG)
    get_url = GetImageUrl(media, storage, 300, Listings(None), Visibility({other.id}))

    with pytest.raises(PermissionDenied):
        get_url.execute(other, asset.id)
