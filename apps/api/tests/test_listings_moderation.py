import uuid

import pytest
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import Engine, inspect, update
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import CommunityMembershipModel, ListingModel
from tests.api_helpers import create_community, join, make_platform_admin, publish_ok, register
from tests.conftest import alembic_config


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
    return publish_ok(client, author, community["id"], title="Anuncio inapropiado")


def set_status(client: TestClient, account: dict, listing_id: str, status: str):
    return client.patch(
        f"/v1/listings/{listing_id}/status", json={"status": status}, headers=account["headers"]
    )


def titles(client: TestClient, account: dict, community_id: str, **params) -> list[str]:
    response = client.get(
        f"/v1/communities/{community_id}/listings", params=params, headers=account["headers"]
    )
    return [item["title"] for item in response.json()["items"]]


@pytest.mark.db
def test_admin_retires_and_restores(
    client: TestClient,
    admin: dict,
    author: dict,
    member: dict,
    community: dict,
    listing: dict,
    db_session: Session,
) -> None:
    retired = set_status(client, admin, listing["id"], "hidden")

    assert retired.status_code == 200
    assert retired.json()["status"] == "hidden"
    row = db_session.get(ListingModel, uuid.UUID(listing["id"]))
    db_session.refresh(row)
    assert str(row.hidden_by) == admin["user"]["id"] and row.hidden_at is not None
    assert titles(client, member, community["id"]) == []
    assert titles(client, member, community["id"], q="inapropiado") == []
    assert client.get(f"/v1/listings/{listing['id']}", headers=member["headers"]).status_code == 404
    for account in (author, admin):
        detail = client.get(f"/v1/listings/{listing['id']}", headers=account["headers"])
        assert detail.json()["status"] == "hidden"

    restored = set_status(client, admin, listing["id"], "active")

    assert restored.json()["status"] == "active"
    db_session.refresh(row)
    assert (row.hidden_by, row.hidden_at) == (None, None)
    assert titles(client, member, community["id"]) == ["Anuncio inapropiado"]


@pytest.mark.db
def test_reserved_and_completed_can_be_retired_and_restore_to_active(
    client: TestClient, admin: dict, listing: dict, db_session: Session
) -> None:
    for status in ("reserved", "completed"):
        db_session.execute(
            update(ListingModel)
            .where(ListingModel.id == uuid.UUID(listing["id"]))
            .values(status=status)
        )
        assert set_status(client, admin, listing["id"], "hidden").status_code == 200
        assert set_status(client, admin, listing["id"], "active").json()["status"] == "active"


@pytest.mark.db
def test_members_and_authors_cannot_moderate(
    client: TestClient, admin: dict, author: dict, member: dict, listing: dict
) -> None:
    outsider_admin = register(client, "otro-admin@example.com")
    create_community(client, outsider_admin, name="Otra comunidad")

    for account in (member, author, outsider_admin):
        assert set_status(client, account, listing["id"], "hidden").status_code == 403


@pytest.mark.db
def test_moderator_and_platform_admin_can_moderate(
    client: TestClient,
    member: dict,
    community: dict,
    listing: dict,
    db_session: Session,
) -> None:
    db_session.execute(
        update(CommunityMembershipModel)
        .where(
            CommunityMembershipModel.community_id == uuid.UUID(community["id"]),
            CommunityMembershipModel.user_id == uuid.UUID(member["user"]["id"]),
        )
        .values(role="moderator")
    )
    platform_admin = register(client, "plataforma@example.com")
    make_platform_admin(db_session, platform_admin)

    assert set_status(client, member, listing["id"], "hidden").status_code == 200
    assert set_status(client, platform_admin, listing["id"], "active").status_code == 200


@pytest.mark.db
def test_invalid_transitions(client: TestClient, admin: dict, listing: dict) -> None:
    same = set_status(client, admin, listing["id"], "active")
    assert (same.status_code, same.json()) == (409, {"detail": "El anuncio ya está en ese estado."})

    set_status(client, admin, listing["id"], "hidden")
    again = set_status(client, admin, listing["id"], "hidden")
    assert again.status_code == 409


@pytest.mark.db
@pytest.mark.parametrize("status", ["deleted", "draft", "otro"])
def test_unsupported_statuses(client: TestClient, admin: dict, listing: dict, status: str) -> None:
    assert set_status(client, admin, listing["id"], status).status_code == 422


@pytest.mark.db
def test_deleted_or_unknown_listing(
    client: TestClient, admin: dict, author: dict, listing: dict
) -> None:
    client.delete(f"/v1/listings/{listing['id']}", headers=author["headers"])

    assert set_status(client, admin, listing["id"], "hidden").status_code == 404
    assert set_status(client, admin, str(uuid.uuid4()), "hidden").status_code == 404
    response = client.patch(f"/v1/listings/{listing['id']}/status", json={"status": "hidden"})
    assert response.status_code == 401


@pytest.mark.db
def test_migration_0006_is_reversible(db_engine: Engine) -> None:
    with db_engine.begin() as connection:
        command.downgrade(alembic_config(connection), "0005")
        columns = {c["name"] for c in inspect(connection).get_columns("listing")}
        assert "hidden_by" not in columns

    with db_engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
        columns = {c["name"] for c in inspect(connection).get_columns("listing")}
        assert {"hidden_by", "hidden_at"} <= columns
