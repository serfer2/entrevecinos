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
from entrevecinos.domain.users.entities import PlatformRole
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
        self.readable: set[tuple[uuid.UUID, uuid.UUID]] = set()

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

    def is_readable_by(self, asset_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return (asset_id, user_id) in self.readable


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


def test_image_url_permissions() -> None:
    media, storage = FakeMediaRepository(), InMemoryObjectStorage()
    owner, member, outsider = make_user(), make_user(), make_user()
    asset = UploadImage(media, storage, max_bytes=1000).execute(owner.id, JPEG)
    media.readable.add((asset.id, member.id))
    get_url = GetImageUrl(media, storage, ttl_seconds=300)

    assert "X-Amz-Expires=300" in get_url.execute(owner, asset.id)
    assert get_url.execute(member, asset.id).startswith("http://localhost:9000/")
    assert get_url.execute(make_user(PlatformRole.PLATFORM_ADMIN), asset.id)
    with pytest.raises(PermissionDenied):
        get_url.execute(outsider, asset.id)
    with pytest.raises(MediaNotFound):
        get_url.execute(owner, uuid.uuid4())
