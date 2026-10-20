import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import CategoryModel, ListingModel
from tests.api_helpers import (
    category_id,
    create_community,
    join,
    listing_body,
    publish,
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
def member(client: TestClient, admin: dict, community: dict) -> dict:
    account = register(client, "vecina@example.com", full_name="Vera Vecina", phone="600111222")
    join(client, admin, account, community["id"])
    return account


def listing_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(ListingModel))


def test_categories_are_active_and_end_with_others(
    client: TestClient, admin: dict, db_session: Session
) -> None:
    db_session.scalars(
        select(CategoryModel).where(CategoryModel.slug == "motor")
    ).one().is_active = False
    db_session.flush()

    items = client.get("/v1/categories", headers=admin["headers"]).json()["items"]

    names = [c["name"] for c in items]
    assert names[-1] == "Otros"
    assert names[:-1] == sorted(names[:-1])
    assert "Motor" not in names
    assert set(items[0]) == {"id", "name", "slug", "is_active"}
    assert client.get("/v1/categories").status_code == 401


def test_publish(client: TestClient, member: dict, community: dict) -> None:
    body = publish_ok(client, member, community["id"], title=" Bicicleta infantil ")

    assert body["title"] == "Bicicleta infantil"
    assert (body["status"], body["type"], body["community_id"]) == (
        "active",
        "sell",
        community["id"],
    )
    assert body["owner"] == {
        "id": member["user"]["id"],
        "full_name": "Vera Vecina",
        "phone": "600111222",
        "avatar_url": None,
    }
    assert body["published_at"] and body["updated_at"]
    assert (body["price"], body["currency"], body["images"]) == (None, None, [])


def test_free_listing_without_price(client: TestClient, member: dict, community: dict) -> None:
    body = publish_ok(client, member, community["id"], type="free")

    assert (body["price"], body["currency"]) == (None, None)


def test_price_defaults_to_eur(client: TestClient, member: dict, community: dict) -> None:
    body = publish_ok(client, member, community["id"], price=45)

    assert (body["price"], body["currency"]) == (45.0, "EUR")
    assert (
        publish_ok(client, member, community["id"], price="12.50", currency="USD")["price"] == 12.5
    )


@pytest.mark.parametrize("count", [1, 3, 10])
def test_images_keep_order_and_first_is_cover(
    client: TestClient, member: dict, community: dict, count: int
) -> None:
    assets = [upload_image(client, member) for _ in range(count)]

    body = publish_ok(client, member, community["id"], image_asset_ids=assets)

    assert [i["asset_id"] for i in body["images"]] == assets
    assert [i["position"] for i in body["images"]] == list(range(count))
    assert [i["is_cover"] for i in body["images"]] == [True] + [False] * (count - 1)
    assert body["images"][0]["url"] == f"/v1/media/{assets[0]}"


def test_listing_images_are_readable_by_members(
    client: TestClient, admin: dict, member: dict, community: dict
) -> None:
    asset = upload_image(client, member)
    publish_ok(client, member, community["id"], image_asset_ids=[asset])

    response = client.get(f"/v1/media/{asset}", headers=admin["headers"], follow_redirects=False)
    assert response.status_code == 302


def test_invalid_images_are_rejected(
    client: TestClient, admin: dict, member: dict, community: dict, db_session: Session
) -> None:
    foreign = upload_image(client, admin)
    used = upload_image(client, member)
    publish_ok(client, member, community["id"], image_asset_ids=[used])
    before = listing_count(db_session)

    for assets in ([foreign], [used], [str(uuid.uuid4())]):
        response = publish(client, member, community["id"], image_asset_ids=assets)
        assert (response.status_code, response.json()) == (
            400,
            {"detail": "Alguna imagen no es válida."},
        )
    assert listing_count(db_session) == before


def test_more_than_ten_or_repeated_images(
    client: TestClient, member: dict, community: dict
) -> None:
    asset = upload_image(client, member)

    many = publish(client, member, community["id"], image_asset_ids=[str(uuid.uuid4())] * 11)
    repeated = publish(client, member, community["id"], image_asset_ids=[asset, asset])

    assert many.status_code == 422 and repeated.status_code == 422


def test_unknown_or_inactive_category(
    client: TestClient, member: dict, community: dict, db_session: Session
) -> None:
    motor = category_id(client, member, "motor")
    db_session.get(CategoryModel, uuid.UUID(motor)).is_active = False
    db_session.flush()

    for category in (str(uuid.uuid4()), motor):
        response = publish(client, member, community["id"], category_id=category)
        assert response.status_code == 422
        assert response.json()["detail"][0]["loc"] == ["body", "category_id"]


def test_required_fields(
    client: TestClient, member: dict, community: dict, db_session: Session
) -> None:
    response = client.post(
        f"/v1/communities/{community['id']}/listings",
        json={"title": "  ", "price": 5},
        headers=member["headers"],
    )

    assert response.status_code == 422
    locs = {tuple(e["loc"]) for e in response.json()["detail"]}
    assert {("body", f) for f in ("title", "description", "category_id", "type")} <= locs
    assert listing_count(db_session) == 0


@pytest.mark.parametrize(
    ("fields", "field"),
    [
        ({"title": "x" * 161}, "title"),
        ({"description": "x" * 5001}, "description"),
        ({"price": -1}, "price"),
        ({"price": "1.234"}, "price"),
        ({"price": 100000000}, "price"),
        ({"currency": "EUR"}, "currency"),
        ({"price": 5, "currency": "eur"}, "currency"),
        ({"type": "rent"}, "type"),
        ({"status": "hidden"}, "status"),
    ],
)
def test_invalid_fields(
    client: TestClient, member: dict, community: dict, fields: dict, field: str
) -> None:
    response = client.post(
        f"/v1/communities/{community['id']}/listings",
        json=listing_body(client, member, **fields),
        headers=member["headers"],
    )

    assert response.status_code == 422
    assert ["body", field] in [e["loc"] for e in response.json()["detail"]]


def test_pending_member_and_outsider_are_forbidden(
    client: TestClient, community: dict, db_session: Session
) -> None:
    pending = register(client, "pendiente@example.com")
    request_access(client, pending, community["id"])
    outsider = register(client, "ajeno@example.com")

    pending_response = publish(client, pending, community["id"])
    outsider_response = publish(client, outsider, community["id"])

    assert pending_response.status_code == 403
    assert pending_response.json()["status"] == "pending"
    assert outsider_response.status_code == 403
    assert "status" not in outsider_response.json()
    assert listing_count(db_session) == 0


def test_unknown_community_and_authentication(client: TestClient, member: dict) -> None:
    assert publish(client, member, str(uuid.uuid4())).status_code == 404
    response = client.post(f"/v1/communities/{uuid.uuid4()}/listings", json={})
    assert response.status_code == 401
