import pytest
from fastapi.testclient import TestClient

from tests.api_helpers import create_community, join, publish_ok, register, review, upload_image

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


@pytest.fixture
def listing(client: TestClient, author: dict, community: dict) -> dict:
    return publish_ok(client, author, community["id"], title="Bicicleta")


def set_status(client: TestClient, account: dict, listing_id: str, status: str):
    return client.patch(
        f"/v1/listings/{listing_id}/status", json={"status": status}, headers=account["headers"]
    )


def titles(client: TestClient, account: dict, community_id: str, **params) -> list[str]:
    response = client.get(
        f"/v1/communities/{community_id}/listings", params=params, headers=account["headers"]
    )
    return [item["title"] for item in response.json()["items"]]


def test_reserve_and_unreserve(
    client: TestClient, author: dict, member: dict, community: dict, listing: dict
) -> None:
    reserved = set_status(client, author, listing["id"], "reserved")

    assert (reserved.status_code, reserved.json()["status"]) == (200, "reserved")
    assert reserved.json()["published_at"] == listing["published_at"]
    assert titles(client, member, community["id"]) == ["Bicicleta"]

    active = set_status(client, author, listing["id"], "active")
    assert active.json()["status"] == "active"


def test_complete_is_final_and_blocks_editing(
    client: TestClient, author: dict, member: dict, community: dict
) -> None:
    asset = upload_image(client, author)
    listing = publish_ok(client, author, community["id"], title="Mesa", image_asset_ids=[asset])
    set_status(client, author, listing["id"], "reserved")

    completed = set_status(client, author, listing["id"], "completed")

    assert completed.json()["status"] == "completed"
    assert titles(client, member, community["id"]) == []
    assert titles(client, member, community["id"], q="mesa") == []
    detail = client.get(f"/v1/listings/{listing['id']}", headers=member["headers"])
    assert detail.json()["status"] == "completed"
    for status in ("active", "reserved"):
        response = set_status(client, author, listing["id"], status)
        assert response.json() == {"detail": "Un anuncio finalizado no puede cambiar de estado."}
    edit = client.patch(
        f"/v1/listings/{listing['id']}", json={"title": "x"}, headers=author["headers"]
    )
    assert (edit.status_code, edit.json()) == (
        403,
        {"detail": "Este anuncio está finalizado y no se puede editar."},
    )
    images = client.put(
        f"/v1/listings/{listing['id']}/images", json={"images": []}, headers=author["headers"]
    )
    assert images.status_code == 403
    deleted = client.delete(f"/v1/listings/{listing['id']}", headers=author["headers"])
    assert deleted.status_code == 204


def test_only_the_author_reserves_or_completes(
    client: TestClient, admin: dict, member: dict, listing: dict
) -> None:
    for account in (member, admin):
        for status in ("reserved", "completed"):
            assert set_status(client, account, listing["id"], status).status_code == 403


def test_blocked_author_and_retired_listing(
    client: TestClient, admin: dict, author: dict, community: dict, listing: dict
) -> None:
    set_status(client, admin, listing["id"], "hidden")
    retired = set_status(client, author, listing["id"], "reserved")
    assert retired.status_code == 403
    set_status(client, admin, listing["id"], "active")

    review(client, admin, community["id"], author["user"]["id"], "blocked")
    assert set_status(client, author, listing["id"], "reserved").status_code == 403


def test_moderation_still_works_on_reserved_listings(
    client: TestClient, admin: dict, author: dict, listing: dict
) -> None:
    set_status(client, author, listing["id"], "reserved")

    assert set_status(client, admin, listing["id"], "hidden").json()["status"] == "hidden"
    assert set_status(client, admin, listing["id"], "active").json()["status"] == "active"
