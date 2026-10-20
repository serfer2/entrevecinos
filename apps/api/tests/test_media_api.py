import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import (
    CategoryModel,
    ListingImageModel,
    ListingModel,
    MediaAssetModel,
)
from tests.api_helpers import create_community, join, register, request_access
from tests.images import GIF, JPEG, PDF, PNG, WEBP

pytestmark = pytest.mark.db

MAX_BYTES = 5 * 1024 * 1024


def upload(
    client: TestClient, account: dict, data: bytes, name="foto.jpg", content_type="image/jpeg"
):
    return client.post(
        "/v1/media", files={"file": (name, data, content_type)}, headers=account["headers"]
    )


@pytest.fixture
def owner(client: TestClient) -> dict:
    return register(client, "autor@example.com")


@pytest.mark.parametrize(
    ("data", "mime"), [(JPEG, "image/jpeg"), (PNG, "image/png"), (WEBP, "image/webp")]
)
def test_upload_valid_images(
    client: TestClient, owner: dict, object_storage, db_session: Session, data: bytes, mime: str
) -> None:
    response = upload(client, owner, data, name="mi vacaciones.jpg", content_type="text/plain")

    assert response.status_code == 201
    body = response.json()
    assert body["mime_type"] == mime
    assert body["size_bytes"] == len(data)
    assert body["url"] == f"/v1/media/{body['id']}"
    stored = db_session.get(MediaAssetModel, uuid.UUID(body["id"]))
    assert "vacaciones" not in stored.object_key
    assert stored.object_key.startswith(f"media/{owner['user']['id']}/")
    assert len(stored.sha256) == 64
    assert object_storage.objects[stored.object_key] == (data, mime)


def test_upload_one_megabyte_jpeg(client: TestClient, owner: dict) -> None:
    data = JPEG + b"\x00" * (1024 * 1024)

    assert upload(client, owner, data).status_code == 201


@pytest.mark.parametrize("data", [PDF, GIF, b"texto renombrado"])
def test_unsupported_types_are_rejected(
    client: TestClient, owner: dict, object_storage, db_session: Session, data: bytes
) -> None:
    response = upload(client, owner, data)

    assert response.status_code == 415
    assert response.json() == {"detail": "Formato no permitido. Usa JPEG, PNG o WebP."}
    assert object_storage.objects == {}
    assert db_session.scalars(select(MediaAssetModel)).all() == []


def test_too_large_is_rejected(client: TestClient, owner: dict, object_storage) -> None:
    data = PNG + b"\x00" * (MAX_BYTES + 1 - len(PNG))

    response = upload(client, owner, data)

    assert response.status_code == 413
    assert response.json() == {"detail": "La imagen supera el tamaño máximo de 5 MB."}
    assert object_storage.objects == {}


def test_exactly_max_size_is_accepted(client: TestClient, owner: dict) -> None:
    assert upload(client, owner, PNG + b"\x00" * (MAX_BYTES - len(PNG))).status_code == 201


def test_huge_content_length_is_rejected_before_reading(client: TestClient, owner: dict) -> None:
    response = client.post(
        "/v1/media",
        content=b"x",
        headers={
            **owner["headers"],
            "Content-Type": "multipart/form-data; boundary=x",
            "Content-Length": str(MAX_BYTES * 3),
        },
    )

    assert response.status_code == 413


def test_empty_or_missing_file(client: TestClient, owner: dict) -> None:
    assert upload(client, owner, b"").status_code == 422
    response = client.post("/v1/media", data={"other": "x"}, headers=owner["headers"])
    assert response.status_code == 422


def test_upload_requires_authentication(client: TestClient) -> None:
    assert (
        client.post("/v1/media", files={"file": ("a.jpg", JPEG, "image/jpeg")}).status_code == 401
    )


def attach_to_listing(db_session: Session, asset_id: str, community: dict, owner: dict, **fields):
    category = db_session.scalars(select(CategoryModel)).first()
    listing = ListingModel(
        community_id=uuid.UUID(community["id"]),
        owner_id=uuid.UUID(owner["user"]["id"]),
        category_id=category.id,
        title="Bicicleta",
        description="Poco uso",
        type="sell",
        **fields,
    )
    db_session.add(listing)
    db_session.flush()
    db_session.add(ListingImageModel(listing_id=listing.id, asset_id=uuid.UUID(asset_id)))
    db_session.flush()
    return listing


def read(client: TestClient, account: dict, asset_id: str):
    return client.get(f"/v1/media/{asset_id}", headers=account["headers"], follow_redirects=False)


def test_uploader_can_read(client: TestClient, owner: dict) -> None:
    asset = upload(client, owner, JPEG).json()

    response = read(client, owner, asset["id"])

    assert response.status_code == 302
    assert response.headers["location"].startswith("http://localhost:9000/")
    assert response.headers["cache-control"] == "private, max-age=270"


@pytest.fixture
def community_with_image(client: TestClient, owner: dict, db_session: Session):
    community = create_community(client, owner)
    asset = upload(client, owner, JPEG).json()
    listing = attach_to_listing(db_session, asset["id"], community, owner)
    return community, asset, listing


def test_approved_member_can_read_listing_image(
    client: TestClient, owner: dict, community_with_image
) -> None:
    community, asset, _ = community_with_image
    member = register(client, "miembro@example.com")
    join(client, owner, member, community["id"])

    assert read(client, member, asset["id"]).status_code == 302


def test_outsider_and_pending_cannot_read(
    client: TestClient, owner: dict, community_with_image
) -> None:
    community, asset, _ = community_with_image
    outsider = register(client, "ajeno@example.com")
    pending = register(client, "pendiente@example.com")
    request_access(client, pending, community["id"])

    for account in (outsider, pending):
        assert read(client, account, asset["id"]).status_code == 403


@pytest.mark.parametrize(
    ("fields", "member_reads"),
    [
        ({"status": "hidden"}, False),
        ({"status": "draft"}, False),
        ({"status": "completed"}, True),
        ({"deleted_at": "now"}, False),
    ],
)
def test_listing_visibility_rules(
    client: TestClient,
    owner: dict,
    db_session: Session,
    fields: dict,
    member_reads: bool,
) -> None:
    from sqlalchemy import func

    community = create_community(client, owner)
    member = register(client, "miembro@example.com")
    join(client, owner, member, community["id"])
    other_author = register(client, "otro@example.com")
    join(client, owner, other_author, community["id"])
    asset = upload(client, other_author, JPEG).json()
    if fields.get("deleted_at") == "now":
        fields = {"deleted_at": func.now()}
    attach_to_listing(db_session, asset["id"], community, other_author, **fields)

    assert (read(client, member, asset["id"]).status_code == 302) is member_reads
    # El administrador de la comunidad ve los retirados, pero no los eliminados.
    expected_admin = "deleted_at" not in fields and fields.get("status") != "draft"
    assert (read(client, owner, asset["id"]).status_code == 302) is expected_admin


def test_unknown_image(client: TestClient, owner: dict) -> None:
    assert read(client, owner, str(uuid.uuid4())).status_code == 404
    assert client.get("/v1/media/x", headers=owner["headers"]).status_code == 422
