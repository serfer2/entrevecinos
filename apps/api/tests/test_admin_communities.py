import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import CommunityModel
from tests.api_helpers import (
    create_community,
    create_pending_community,
    make_platform_admin,
    register,
)

pytestmark = pytest.mark.db


@pytest.fixture
def neighbour(client: TestClient) -> dict:
    return register(client, "vecino@example.com")


@pytest.fixture
def platform_admin(client: TestClient, db_session: Session) -> dict:
    account = register(client, "admin@example.com")
    make_platform_admin(db_session, account)
    return account


def set_creation_order(db_session: Session, *communities: dict) -> None:
    """`now()` es el mismo en toda la transacción de la prueba: fija fechas distintas."""
    base = datetime(2026, 1, 1, tzinfo=UTC)
    for days, community in enumerate(communities):
        db_session.get(CommunityModel, uuid.UUID(community["id"])).created_at = base + timedelta(
            days=days
        )
    db_session.flush()


def approve(client: TestClient, account: dict, community_id: object, body: dict | None = None):
    return client.patch(
        f"/v1/admin/communities/{community_id}",
        json={"is_active": True} if body is None else body,
        headers=account["headers"],
    )


def test_lists_pending_communities_oldest_first(
    client: TestClient, neighbour: dict, platform_admin: dict, db_session: Session
) -> None:
    second = create_pending_community(client, neighbour, name="Segunda")
    active = create_community(client, neighbour, name="Activa")
    first = create_pending_community(client, neighbour, name="Primera")
    set_creation_order(db_session, first, active, second)

    response = client.get(
        "/v1/admin/communities", params={"is_active": "false"}, headers=platform_admin["headers"]
    )

    assert response.status_code == 200
    body = response.json()
    assert [c["id"] for c in body["items"]] == [first["id"], second["id"]]
    assert (body["total"], body["page"]) == (2, 1)


def test_lists_all_communities_without_filter(
    client: TestClient, neighbour: dict, platform_admin: dict, db_session: Session
) -> None:
    pending = create_pending_community(client, neighbour, name="Pendiente")
    active = create_community(client, neighbour, name="Activa")
    set_creation_order(db_session, pending, active)

    response = client.get(
        "/v1/admin/communities", params={"page_size": 1}, headers=platform_admin["headers"]
    )

    assert response.json()["total"] == 2
    assert [c["name"] for c in response.json()["items"]] == ["Pendiente"]


def test_approves_a_pending_community(
    client: TestClient, neighbour: dict, platform_admin: dict
) -> None:
    community = create_pending_community(client, neighbour)

    response = approve(client, platform_admin, community["id"])

    assert response.status_code == 200
    assert response.json() == {**community, "is_active": True}
    detail = client.get(f"/v1/communities/{community['id']}", headers=neighbour["headers"])
    assert detail.status_code == 200
    search = client.get("/v1/communities", headers=neighbour["headers"]).json()
    assert [c["id"] for c in search["items"]] == [community["id"]]


def test_approving_an_active_community_changes_nothing(
    client: TestClient, neighbour: dict, platform_admin: dict
) -> None:
    community = create_community(client, neighbour)

    response = approve(client, platform_admin, community["id"])

    assert response.status_code == 200
    assert response.json() == community


def test_platform_admin_creates_active_communities(
    client: TestClient, platform_admin: dict, neighbour: dict
) -> None:
    response = client.post(
        "/v1/communities", json={"name": "Barrio"}, headers=platform_admin["headers"]
    )

    assert response.status_code == 201
    community = response.json()
    assert community["is_active"] is True
    detail = client.get(f"/v1/communities/{community['id']}", headers=neighbour["headers"])
    assert detail.status_code == 200
    search = client.get("/v1/communities", headers=neighbour["headers"]).json()
    assert [c["id"] for c in search["items"]] == [community["id"]]
    mine = client.get("/v1/users/me/memberships", headers=platform_admin["headers"]).json()
    assert [(m["community"]["id"], m["role"]) for m in mine["items"]] == [
        (community["id"], "community_admin")
    ]


def test_unknown_community_is_not_found(client: TestClient, platform_admin: dict) -> None:
    assert approve(client, platform_admin, uuid.uuid4()).status_code == 404


@pytest.mark.parametrize("body", [{"is_active": False}, {}, {"is_active": True, "name": "X"}])
def test_only_approval_is_supported(
    client: TestClient, neighbour: dict, platform_admin: dict, body: dict
) -> None:
    community = create_pending_community(client, neighbour)

    assert approve(client, platform_admin, community["id"], body).status_code == 422


def test_only_platform_admins_can_review(client: TestClient, neighbour: dict) -> None:
    community = create_pending_community(client, neighbour)

    listing = client.get("/v1/admin/communities", headers=neighbour["headers"])

    assert listing.status_code == 403
    assert approve(client, neighbour, community["id"]).status_code == 403
    detail = client.get(f"/v1/communities/{community['id']}", headers=neighbour["headers"])
    assert detail.status_code == 404


def test_requires_authentication(client: TestClient, neighbour: dict) -> None:
    community = create_pending_community(client, neighbour)

    assert client.get("/v1/admin/communities").status_code == 401
    assert (
        client.patch(
            f"/v1/admin/communities/{community['id']}", json={"is_active": True}
        ).status_code
        == 401
    )
