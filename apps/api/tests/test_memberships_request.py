import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from entrevecinos.domain.communities.errors import MembershipAlreadyExists
from entrevecinos.infrastructure.communities.sqlalchemy_membership_repository import (
    SqlAlchemyMembershipRepository,
)
from entrevecinos.infrastructure.db.models import CommunityMembershipModel, CommunityModel
from tests.api_helpers import create_community, register

pytestmark = pytest.mark.db


@pytest.fixture
def admin(client: TestClient) -> dict:
    return register(client, "admin@example.com", full_name="Ana Admin")


@pytest.fixture
def neighbour(client: TestClient) -> dict:
    return register(client, "vecino@example.com", full_name="Víctor Vecino")


@pytest.fixture
def community(client: TestClient, admin: dict) -> dict:
    return create_community(client, admin, name="Los Olivos")


def request_access(client: TestClient, account: dict, community_id: str):
    return client.post(f"/v1/communities/{community_id}/memberships", headers=account["headers"])


def my_memberships(client: TestClient, account: dict, **params: str) -> list[dict]:
    response = client.get("/v1/users/me/memberships", params=params, headers=account["headers"])
    assert response.status_code == 200
    return response.json()["items"]


def test_request_creates_pending_membership(
    client: TestClient, neighbour: dict, community: dict
) -> None:
    response = request_access(client, neighbour, community["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["community_id"] == community["id"]
    assert body["user"] == {
        "id": neighbour["user"]["id"],
        "full_name": "Víctor Vecino",
        "avatar_url": None,
    }
    assert (body["role"], body["status"]) == ("member", "pending")
    assert body["requested_at"] is not None
    assert (body["reviewed_by"], body["reviewed_at"], body["joined_at"]) == (None, None, None)

    [mine] = my_memberships(client, neighbour)
    assert mine["community"] == community
    assert (mine["role"], mine["status"], mine["joined_at"]) == ("member", "pending", None)


@pytest.mark.parametrize("status", ["pending", "approved", "rejected", "blocked"])
def test_duplicate_request_returns_current_status(
    client: TestClient, neighbour: dict, community: dict, db_session: Session, status: str
) -> None:
    request_access(client, neighbour, community["id"])
    model = db_session.get(
        CommunityMembershipModel, (uuid.UUID(community["id"]), uuid.UUID(neighbour["user"]["id"]))
    )
    model.status = status
    model.joined_at = datetime.now(UTC)
    db_session.flush()

    response = request_access(client, neighbour, community["id"])

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Ya tienes una membresía en esta comunidad.",
        "status": status,
    }
    total = db_session.scalar(select(func.count()).select_from(CommunityMembershipModel))
    assert total == 2  # la del administrador y la del vecino


def test_admin_cannot_request_own_community(
    client: TestClient, admin: dict, community: dict
) -> None:
    response = request_access(client, admin, community["id"])

    assert response.status_code == 409
    assert response.json()["status"] == "approved"


def test_race_on_primary_key_is_a_conflict(
    client: TestClient, neighbour: dict, community: dict, db_session: Session
) -> None:
    request_access(client, neighbour, community["id"])
    repository = SqlAlchemyMembershipRepository(db_session)

    with pytest.raises(MembershipAlreadyExists) as error:
        repository.add_request(uuid.UUID(community["id"]), uuid.UUID(neighbour["user"]["id"]))
    assert error.value.status == "pending"
    db_session.flush()  # la sesión sigue usable tras el savepoint


def test_missing_or_inactive_community_is_not_found(
    client: TestClient, neighbour: dict, community: dict, db_session: Session
) -> None:
    assert request_access(client, neighbour, str(uuid.uuid4())).status_code == 404
    db_session.get(CommunityModel, uuid.UUID(community["id"])).is_active = False
    db_session.flush()

    assert request_access(client, neighbour, community["id"]).status_code == 404


def test_my_memberships_filters_and_orders(
    client: TestClient, admin: dict, neighbour: dict, community: dict
) -> None:
    other = create_community(client, admin, name="Barrio del Pilar")
    request_access(client, neighbour, community["id"])
    request_access(client, neighbour, other["id"])
    own = create_community(client, neighbour, name="Mi comunidad")

    assert [m["community"]["id"] for m in my_memberships(client, neighbour)] == [
        own["id"],
        other["id"],
        community["id"],
    ]
    approved = my_memberships(client, neighbour, status="approved")
    assert [(m["community"]["id"], m["role"]) for m in approved] == [(own["id"], "community_admin")]
    assert approved[0]["joined_at"] is not None


def test_inactive_communities_only_for_approved_memberships(
    client: TestClient, admin: dict, neighbour: dict, community: dict, db_session: Session
) -> None:
    request_access(client, neighbour, community["id"])
    db_session.get(CommunityModel, uuid.UUID(community["id"])).is_active = False
    db_session.flush()

    assert my_memberships(client, neighbour) == []
    assert [m["community"]["id"] for m in my_memberships(client, admin)] == [community["id"]]


def test_invalid_status_filter(client: TestClient, neighbour: dict) -> None:
    response = client.get(
        "/v1/users/me/memberships", params={"status": "otro"}, headers=neighbour["headers"]
    )
    assert response.status_code == 422


def test_requires_authentication(client: TestClient, community: dict) -> None:
    assert client.post(f"/v1/communities/{community['id']}/memberships").status_code == 401
    assert client.get("/v1/users/me/memberships").status_code == 401
