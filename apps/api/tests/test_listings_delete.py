import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import ListingModel
from tests.api_helpers import (
    create_community,
    join,
    make_platform_admin,
    publish_ok,
    register,
    upload_image,
)

pytestmark = pytest.mark.db


@pytest.fixture
def admin(client: TestClient) -> dict:
    return register(client, "admin@example.com")


@pytest.fixture
def community(client: TestClient, admin: dict) -> dict:
    return create_community(client, admin)


@pytest.fixture
def author(client: TestClient, admin: dict, community: dict) -> dict:
    account = register(client, "autor@example.com")
    join(client, admin, account, community["id"])
    return account


@pytest.fixture
def member(client: TestClient, admin: dict, community: dict) -> dict:
    account = register(client, "miembro@example.com")
    join(client, admin, account, community["id"])
    return account


def delete(client: TestClient, account: dict, listing_id: str):
    return client.delete(f"/v1/listings/{listing_id}", headers=account["headers"])


def read_image(client: TestClient, account: dict, asset_id: str) -> int:
    return client.get(
        f"/v1/media/{asset_id}", headers=account["headers"], follow_redirects=False
    ).status_code


def test_author_deletes(
    client: TestClient, author: dict, member: dict, community: dict, db_session: Session
) -> None:
    asset = upload_image(client, author)
    listing = publish_ok(client, author, community["id"], image_asset_ids=[asset])
    assert read_image(client, member, asset) == 302

    response = delete(client, author, listing["id"])

    assert response.status_code == 204
    assert response.content == b""
    db_session.expire_all()
    row = db_session.get(ListingModel, uuid.UUID(listing["id"]))
    assert row.deleted_at is not None and row.status == "deleted"
    assert read_image(client, member, asset) == 403
    assert read_image(client, author, asset) == 302  # quien la subió la sigue viendo


def test_deleting_twice_is_not_found(client: TestClient, author: dict, community: dict) -> None:
    listing = publish_ok(client, author, community["id"])
    delete(client, author, listing["id"])

    assert delete(client, author, listing["id"]).status_code == 404
    assert delete(client, author, str(uuid.uuid4())).status_code == 404


def test_member_and_outsider_cannot_delete(
    client: TestClient, author: dict, member: dict, community: dict, db_session: Session
) -> None:
    listing = publish_ok(client, author, community["id"])
    other_admin = register(client, "otro-admin@example.com")
    create_community(client, other_admin, name="Otra comunidad")

    for account in (member, other_admin):
        assert delete(client, account, listing["id"]).status_code == 403
    assert db_session.get(ListingModel, uuid.UUID(listing["id"])).deleted_at is None


def test_community_admin_and_platform_admin_can_delete(
    client: TestClient, admin: dict, author: dict, community: dict, db_session: Session
) -> None:
    first = publish_ok(client, author, community["id"])
    second = publish_ok(client, author, community["id"])
    platform_admin = register(client, "plataforma@example.com")
    make_platform_admin(db_session, platform_admin)

    assert delete(client, admin, first["id"]).status_code == 204
    assert delete(client, platform_admin, second["id"]).status_code == 204


def test_requires_authentication(client: TestClient, author: dict, community: dict) -> None:
    listing = publish_ok(client, author, community["id"])

    assert client.delete(f"/v1/listings/{listing['id']}").status_code == 401
    assert client.delete("/v1/listings/x", headers=author["headers"]).status_code == 422
