import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import CommunityMembershipModel, CommunityModel
from tests.api_helpers import create_community, register

pytestmark = pytest.mark.db


@pytest.fixture
def account(client: TestClient) -> dict:
    return register(client, "vecino@example.com")


def test_creates_community_with_creator_as_approved_admin(
    client: TestClient, account: dict, db_session: Session
) -> None:
    response = client.post(
        "/v1/communities",
        json={"name": " Urbanización Los Olivos ", "city": "Majadahonda", "postal_code": "28220"},
        headers=account["headers"],
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Urbanización Los Olivos"
    assert (body["city"], body["postal_code"], body["description"]) == (
        "Majadahonda",
        "28220",
        None,
    )
    assert body["created_by"] == account["user"]["id"]
    assert body["is_active"] is True
    membership = db_session.scalars(select(CommunityMembershipModel)).one()
    assert str(membership.community_id) == body["id"]
    assert str(membership.user_id) == account["user"]["id"]
    assert (membership.role, membership.status) == ("community_admin", "approved")
    assert membership.joined_at is not None
    assert str(membership.reviewed_by) == account["user"]["id"]


def test_blank_optional_fields_are_null(client: TestClient, account: dict) -> None:
    body = create_community(client, account, description="  ", city="", postal_code=" ")

    assert (body["description"], body["city"], body["postal_code"]) == (None, None, None)


@pytest.mark.parametrize("body", [{"name": ""}, {"name": "   "}, {}, {"name": None}])
def test_name_is_required(
    client: TestClient, account: dict, db_session: Session, body: dict
) -> None:
    response = client.post("/v1/communities", json=body, headers=account["headers"])

    assert response.status_code == 422
    assert ["body", "name"] in [error["loc"] for error in response.json()["detail"]]
    assert db_session.scalars(select(CommunityModel)).all() == []
    assert db_session.scalars(select(CommunityMembershipModel)).all() == []


@pytest.mark.parametrize(
    "body",
    [
        {"name": "x" * 121},
        {"name": "X", "description": "x" * 2001},
        {"name": "X", "postal_code": "1" * 17},
        {"name": "X", "city": "x" * 121},
        {"name": "X", "is_active": False},
    ],
)
def test_rejects_invalid_fields(client: TestClient, account: dict, body: dict) -> None:
    assert client.post("/v1/communities", json=body, headers=account["headers"]).status_code == 422


def test_any_authenticated_user_can_get_a_community(client: TestClient, account: dict) -> None:
    community = create_community(client, account, city="Majadahonda")
    other = register(client, "otra@example.com")

    response = client.get(f"/v1/communities/{community['id']}", headers=other["headers"])

    assert response.status_code == 200
    assert response.json() == community


def test_missing_or_inactive_community_is_not_found(
    client: TestClient, account: dict, db_session: Session
) -> None:
    community = create_community(client, account)
    db_session.get(CommunityModel, uuid.UUID(community["id"])).is_active = False
    db_session.flush()

    for community_id in (community["id"], uuid.uuid4()):
        response = client.get(f"/v1/communities/{community_id}", headers=account["headers"])
        assert response.status_code == 404
        assert response.json() == {"detail": "Recurso no encontrado."}


def test_malformed_id_is_a_validation_error(client: TestClient, account: dict) -> None:
    assert client.get("/v1/communities/no-es-uuid", headers=account["headers"]).status_code == 422


def test_requires_authentication(client: TestClient, account: dict) -> None:
    community = create_community(client, account)

    assert client.post("/v1/communities", json={"name": "X"}).status_code == 401
    assert client.get(f"/v1/communities/{community['id']}").status_code == 401
