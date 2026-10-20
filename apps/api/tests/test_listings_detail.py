import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import ListingModel, UserModel
from tests.api_helpers import (
    create_community,
    join,
    make_platform_admin,
    publish_ok,
    register,
    request_access,
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
    account = register(client, "autor@example.com", full_name="Ana Autora", phone="600111222")
    join(client, admin, account, community["id"])
    return account


@pytest.fixture
def member(client: TestClient, admin: dict, community: dict) -> dict:
    account = register(client, "miembro@example.com")
    join(client, admin, account, community["id"])
    return account


def detail(client: TestClient, account: dict, listing_id: str):
    return client.get(f"/v1/listings/{listing_id}", headers=account["headers"])


def set_status(db_session: Session, listing_id: str, status: str) -> None:
    db_session.execute(
        update(ListingModel).where(ListingModel.id == uuid.UUID(listing_id)).values(status=status)
    )


def test_member_sees_full_listing(
    client: TestClient, author: dict, member: dict, community: dict
) -> None:
    assets = [upload_image(client, author) for _ in range(2)]
    published = publish_ok(client, author, community["id"], price=45, image_asset_ids=assets)

    response = detail(client, member, published["id"])

    assert response.status_code == 200
    body = response.json()
    assert body == published
    assert body["owner"]["full_name"] == "Ana Autora"
    assert body["owner"]["phone"] == "600111222"
    assert [i["asset_id"] for i in body["images"]] == assets


def test_owner_profile_changes_are_reflected(
    client: TestClient, author: dict, member: dict, community: dict
) -> None:
    published = publish_ok(client, author, community["id"])
    client.patch("/v1/users/me", json={"phone": None}, headers=author["headers"])

    assert detail(client, member, published["id"]).json()["owner"]["phone"] is None


def test_completed_is_still_visible(
    client: TestClient, author: dict, member: dict, community: dict, db_session: Session
) -> None:
    published = publish_ok(client, author, community["id"])
    set_status(db_session, published["id"], "completed")

    assert detail(client, member, published["id"]).json()["status"] == "completed"


def test_hidden_listing_visibility(
    client: TestClient,
    admin: dict,
    author: dict,
    member: dict,
    community: dict,
    db_session: Session,
) -> None:
    published = publish_ok(client, author, community["id"])
    set_status(db_session, published["id"], "hidden")
    platform_admin = register(client, "plataforma@example.com")
    make_platform_admin(db_session, platform_admin)

    assert detail(client, member, published["id"]).status_code == 404
    assert detail(client, member, published["id"]).json() == {"detail": "Recurso no encontrado."}
    for account in (author, admin, platform_admin):
        assert detail(client, account, published["id"]).json()["status"] == "hidden"


def test_deleted_and_unknown_are_not_found(
    client: TestClient, author: dict, member: dict, community: dict
) -> None:
    published = publish_ok(client, author, community["id"])
    client.delete(f"/v1/listings/{published['id']}", headers=author["headers"])

    assert detail(client, member, published["id"]).status_code == 404
    assert detail(client, author, published["id"]).status_code == 404
    assert detail(client, member, str(uuid.uuid4())).status_code == 404
    assert detail(client, member, "no-es-uuid").status_code == 422


def test_deleted_account_listings_are_hidden(
    client: TestClient, author: dict, member: dict, community: dict, db_session: Session
) -> None:
    published = publish_ok(client, author, community["id"])
    db_session.execute(
        update(UserModel)
        .where(UserModel.id == uuid.UUID(author["user"]["id"]))
        .values(deleted_at=UserModel.created_at)
    )

    assert detail(client, member, published["id"]).status_code == 404
    listing = client.get(f"/v1/communities/{community['id']}/listings", headers=member["headers"])
    assert listing.json()["total"] == 0


def test_non_members_are_forbidden(client: TestClient, author: dict, community: dict) -> None:
    published = publish_ok(client, author, community["id"])
    pending = register(client, "pendiente@example.com")
    request_access(client, pending, community["id"])
    outsider = register(client, "ajeno@example.com")

    pending_response = detail(client, pending, published["id"])
    assert (pending_response.status_code, pending_response.json()["status"]) == (403, "pending")
    assert detail(client, outsider, published["id"]).status_code == 403
    assert client.get(f"/v1/listings/{published['id']}").status_code == 401
