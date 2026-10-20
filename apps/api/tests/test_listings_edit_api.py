import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import CategoryModel, ListingModel
from tests.api_helpers import (
    category_id,
    create_community,
    join,
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
def listing(client: TestClient, author: dict, community: dict) -> dict:
    return publish_ok(client, author, community["id"], price=45)


def patch(client: TestClient, account: dict, listing_id: str, body: object):
    return client.patch(f"/v1/listings/{listing_id}", json=body, headers=account["headers"])


def put_images(client: TestClient, account: dict, listing_id: str, images: list):
    return client.put(
        f"/v1/listings/{listing_id}/images", json={"images": images}, headers=account["headers"]
    )


def test_author_edits_fields(client: TestClient, author: dict, listing: dict) -> None:
    response = patch(
        client,
        author,
        listing["id"],
        {"title": ' Bicicleta infantil 16" ', "price": 40, "type": "free", "description": "Otra"},
    )

    assert response.status_code == 200
    body = response.json()
    assert (body["title"], body["price"], body["currency"], body["type"]) == (
        'Bicicleta infantil 16"',
        40.0,
        "EUR",
        "free",
    )
    assert body["description"] == "Otra"
    assert body["published_at"] == listing["published_at"]
    assert body["updated_at"] > listing["updated_at"]
    detail = client.get(f"/v1/listings/{listing['id']}", headers=author["headers"]).json()
    assert detail == body


def test_partial_and_price_removal(client: TestClient, author: dict, listing: dict) -> None:
    other = category_id(client, author, "motor")

    first = patch(client, author, listing["id"], {"category_id": other}).json()
    second = patch(client, author, listing["id"], {"price": None}).json()

    assert (first["category_id"], first["title"], first["price"]) == (other, listing["title"], 45.0)
    assert (second["price"], second["currency"]) == (None, None)


@pytest.mark.parametrize(
    ("body", "field"),
    [
        ({"title": "  "}, "title"),
        ({"title": None}, "title"),
        ({"description": None}, "description"),
        ({"category_id": None}, "category_id"),
        ({"type": None}, "type"),
        ({"price": -1}, "price"),
        ({"status": "hidden"}, "status"),
    ],
)
def test_validation_keeps_listing(
    client: TestClient, author: dict, listing: dict, db_session: Session, body: dict, field: str
) -> None:
    response = patch(client, author, listing["id"], body)

    assert response.status_code == 422
    assert ["body", field] in [e["loc"] for e in response.json()["detail"]]
    row = db_session.get(ListingModel, uuid.UUID(listing["id"]))
    assert (row.title, row.status) == (listing["title"], "active")


def test_currency_without_price_and_inactive_category(
    client: TestClient, author: dict, community: dict, db_session: Session
) -> None:
    free = publish_ok(client, author, community["id"], type="free")
    motor = category_id(client, author, "motor")
    db_session.get(CategoryModel, uuid.UUID(motor)).is_active = False
    db_session.flush()

    currency = patch(client, author, free["id"], {"currency": "EUR"})
    category = patch(client, author, free["id"], {"category_id": motor})

    assert currency.json()["detail"][0]["loc"] == ["body", "currency"]
    assert category.json()["detail"][0]["loc"] == ["body", "category_id"]
    assert patch(client, author, free["id"], {}).status_code == 422


def test_only_the_author_can_edit(
    client: TestClient, admin: dict, author: dict, community: dict, listing: dict
) -> None:
    member = register(client, "miembro@example.com")
    join(client, admin, member, community["id"])

    for account in (member, admin):
        assert patch(client, account, listing["id"], {"title": "x"}).status_code == 403
        assert put_images(client, account, listing["id"], []).status_code == 403
    assert (
        client.get(f"/v1/listings/{listing['id']}", headers=admin["headers"]).json()["title"]
        == (listing["title"])
    )


def test_hidden_and_deleted(
    client: TestClient, author: dict, listing: dict, db_session: Session
) -> None:
    db_session.execute(
        update(ListingModel)
        .where(ListingModel.id == uuid.UUID(listing["id"]))
        .values(status="hidden")
    )

    response = patch(client, author, listing["id"], {"title": "x"})
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Este anuncio ha sido retirado por la administración de la comunidad."
    }

    db_session.execute(
        update(ListingModel)
        .where(ListingModel.id == uuid.UUID(listing["id"]))
        .values(status="active")
    )
    client.delete(f"/v1/listings/{listing['id']}", headers=author["headers"])
    assert patch(client, author, listing["id"], {"title": "x"}).status_code == 404


def test_replace_images(client: TestClient, author: dict, community: dict) -> None:
    a, b, c = (upload_image(client, author) for _ in range(3))
    listing = publish_ok(client, author, community["id"], image_asset_ids=[a, b])

    reordered = put_images(
        client, author, listing["id"], [{"asset_id": b, "is_cover": True}, {"asset_id": a}]
    )
    added = put_images(
        client, author, listing["id"], [{"asset_id": a}, {"asset_id": c}, {"asset_id": b}]
    )
    removed = put_images(client, author, listing["id"], [])

    assert [(i["asset_id"], i["is_cover"]) for i in reordered.json()["images"]] == [
        (b, True),
        (a, False),
    ]
    assert [(i["asset_id"], i["position"], i["is_cover"]) for i in added.json()["images"]] == [
        (a, 0, True),
        (c, 1, False),
        (b, 2, False),
    ]
    assert removed.json()["images"] == []


def test_replace_images_validation(
    client: TestClient, admin: dict, author: dict, community: dict
) -> None:
    own = upload_image(client, author)
    foreign = upload_image(client, admin)
    used = upload_image(client, author)
    publish_ok(client, author, community["id"], image_asset_ids=[used])
    listing = publish_ok(client, author, community["id"])

    for asset in (foreign, used, str(uuid.uuid4())):
        response = put_images(client, author, listing["id"], [{"asset_id": asset}])
        assert response.status_code == 400
    two_covers = [{"asset_id": own, "is_cover": True}, {"asset_id": used, "is_cover": True}]
    assert put_images(client, author, listing["id"], two_covers).status_code == 422
    many = [{"asset_id": str(uuid.uuid4())} for _ in range(11)]
    assert put_images(client, author, listing["id"], many).status_code == 422
    assert put_images(client, author, listing["id"], [{"asset_id": own}] * 2).status_code == 422
