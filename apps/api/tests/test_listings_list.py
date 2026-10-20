import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, update
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import ListingModel
from tests.api_helpers import (
    create_community,
    join,
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
    account = register(client, "miembro@example.com")
    join(client, admin, account, community["id"])
    return account


def listings(client: TestClient, account: dict, community_id: str, **params: object):
    return client.get(
        f"/v1/communities/{community_id}/listings", params=params, headers=account["headers"]
    )


def set_published(db_session: Session, listing_id: str, when: datetime) -> None:
    db_session.execute(
        update(ListingModel)
        .where(ListingModel.id == uuid.UUID(listing_id))
        .values(published_at=when)
    )


def test_lists_visible_listings_newest_first(
    client: TestClient, admin: dict, member: dict, community: dict, db_session: Session
) -> None:
    base = datetime(2026, 10, 1, tzinfo=UTC)
    created = [publish_ok(client, member, community["id"], title=f"Anuncio {n}") for n in range(3)]
    for days, listing in zip((2, 0, 1), created, strict=True):
        set_published(db_session, listing["id"], base + timedelta(days=days))

    body = listings(client, admin, community["id"]).json()

    assert [i["title"] for i in body["items"]] == ["Anuncio 0", "Anuncio 2", "Anuncio 1"]
    assert (body["total"], body["page"], body["page_size"]) == (3, 1, 20)
    item = body["items"][0]
    assert {"title", "type", "price", "images", "published_at", "owner"} <= set(item)


def test_tie_breaker_is_stable_across_pages(
    client: TestClient, member: dict, community: dict, db_session: Session
) -> None:
    same = datetime(2026, 10, 1, tzinfo=UTC)
    ids = [publish_ok(client, member, community["id"])["id"] for _ in range(5)]
    for listing_id in ids:
        set_published(db_session, listing_id, same)

    pages = [
        listings(client, member, community["id"], page=n, page_size=2).json() for n in (1, 2, 3)
    ]

    seen = [i["id"] for p in pages for i in p["items"]]
    assert sorted(seen) == sorted(ids) and len(seen) == 5
    assert seen == sorted(ids, reverse=True)
    assert [len(p["items"]) for p in pages] == [2, 2, 1]
    assert all(p["total"] == 5 for p in pages)


def test_only_active_and_reserved_of_this_community(
    client: TestClient, admin: dict, member: dict, community: dict, db_session: Session
) -> None:
    visible = {
        status: publish_ok(client, member, community["id"], title=status)["id"]
        for status in ("active", "reserved", "hidden", "completed", "draft")
    }
    for status, listing_id in visible.items():
        db_session.execute(
            update(ListingModel)
            .where(ListingModel.id == uuid.UUID(listing_id))
            .values(status=status)
        )
    deleted = publish_ok(client, member, community["id"], title="borrado")
    client.delete(f"/v1/listings/{deleted['id']}", headers=member["headers"])
    other = create_community(client, admin, name="Otra")
    publish_ok(client, admin, other["id"], title="de otra comunidad")

    body = listings(client, member, community["id"]).json()

    assert sorted(i["title"] for i in body["items"]) == ["active", "reserved"]
    assert body["total"] == 2


def test_empty_community(client: TestClient, member: dict, community: dict) -> None:
    body = listings(client, member, community["id"]).json()

    assert (body["items"], body["total"]) == ([], 0)


def test_access_is_restricted(client: TestClient, community: dict) -> None:
    pending = register(client, "pendiente@example.com")
    request_access(client, pending, community["id"])
    outsider = register(client, "ajeno@example.com")

    pending_response = listings(client, pending, community["id"])
    assert (pending_response.status_code, pending_response.json()["status"]) == (403, "pending")
    assert listings(client, outsider, community["id"]).status_code == 403
    assert listings(client, outsider, str(uuid.uuid4())).status_code == 404
    assert client.get(f"/v1/communities/{community['id']}/listings").status_code == 401


@pytest.mark.parametrize("param", ["sort", "order"])
def test_pending_parameters_are_rejected(
    client: TestClient, member: dict, community: dict, param: str
) -> None:
    response = listings(client, member, community["id"], **{param: "x"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", param]


def count_statements(db_session: Session, call) -> int:
    statements: list[str] = []

    def record(conn, cursor, statement, *args):
        statements.append(statement)

    connection = db_session.connection()
    event.listen(connection, "before_cursor_execute", record)
    try:
        call()
    finally:
        event.remove(connection, "before_cursor_execute", record)
    return len(statements)


def test_fixed_number_of_queries(
    client: TestClient, member: dict, community: dict, db_session: Session
) -> None:
    publish_ok(client, member, community["id"], image_asset_ids=[upload_image(client, member)])
    one = count_statements(db_session, lambda: listings(client, member, community["id"]))
    for _ in range(9):
        assets = [upload_image(client, member) for _ in range(3)]
        publish_ok(client, member, community["id"], image_asset_ids=assets)

    ten = count_statements(db_session, lambda: listings(client, member, community["id"]))

    assert ten == one
