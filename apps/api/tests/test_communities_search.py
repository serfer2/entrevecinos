import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import CommunityModel
from tests.api_helpers import create_community, register

pytestmark = pytest.mark.db


@pytest.fixture
def account(client: TestClient) -> dict:
    return register(client, "vecino@example.com")


@pytest.fixture
def two_communities(client: TestClient, account: dict) -> tuple[dict, dict]:
    olivos = create_community(
        client,
        account,
        name="Urbanización Los Olivos",
        city="Majadahonda",
        postal_code="28220",
        description="Fases 1 a 3",
    )
    pilar = create_community(
        client, account, name="Barrio del Pilar", city="Madrid", postal_code="28029"
    )
    return olivos, pilar


def search(client: TestClient, account: dict, **params: object):
    return client.get("/v1/communities", params=params, headers=account["headers"])


@pytest.mark.parametrize(
    "params",
    [
        {"q": "olivos"},
        {"q": "Olívos"},
        {"q": "URBANIZACION"},
        {"q": "fases"},
        {"city": "majadahonda"},
        {"postal_code": "28220"},
        {"q": "olivos", "city": "Majadahonda", "postal_code": "282"},
    ],
)
def test_finds_matching_community(
    client: TestClient, account: dict, two_communities: tuple[dict, dict], params: dict
) -> None:
    olivos, _ = two_communities

    body = search(client, account, **params).json()

    assert [c["id"] for c in body["items"]] == [olivos["id"]]
    assert (body["total"], body["page"], body["page_size"]) == (1, 1, 20)


def test_postal_code_matches_by_prefix_and_orders_by_name(
    client: TestClient, account: dict, two_communities: tuple[dict, dict]
) -> None:
    olivos, pilar = two_communities

    body = search(client, account, postal_code="28").json()

    assert [c["id"] for c in body["items"]] == [pilar["id"], olivos["id"]]


def test_filters_combine_with_and(
    client: TestClient, account: dict, two_communities: tuple[dict, dict]
) -> None:
    assert search(client, account, q="olivos", city="Madrid").json()["total"] == 0


def test_wildcards_are_literal(
    client: TestClient, account: dict, two_communities: tuple[dict, dict]
) -> None:
    assert search(client, account, q="%").json()["total"] == 0
    assert search(client, account, q="_").json()["total"] == 0


def test_blank_filters_are_ignored(
    client: TestClient, account: dict, two_communities: tuple[dict, dict]
) -> None:
    assert search(client, account, q="  ", city="").json()["total"] == 2


def test_inactive_communities_are_hidden(
    client: TestClient, account: dict, two_communities: tuple[dict, dict], db_session: Session
) -> None:
    olivos, _ = two_communities
    db_session.get(CommunityModel, uuid.UUID(olivos["id"])).is_active = False
    db_session.flush()

    assert search(client, account, q="olivos").json()["total"] == 0


def test_pagination(client: TestClient, account: dict) -> None:
    for number in range(25):
        create_community(client, account, name=f"Comunidad {number:02d}")

    body = search(client, account, page=2, page_size=10).json()

    assert [c["name"] for c in body["items"]] == [f"Comunidad {n}" for n in range(10, 20)]
    assert (body["page"], body["page_size"], body["total"]) == (2, 10, 25)
    beyond = search(client, account, page=4, page_size=10).json()
    assert (beyond["items"], beyond["total"]) == ([], 25)


@pytest.mark.parametrize(
    "params",
    [
        {"page_size": 101},
        {"page_size": 0},
        {"page": 0},
        {"q": "x" * 161},
        {"postal_code": "1" * 17},
    ],
)
def test_rejects_invalid_parameters(client: TestClient, account: dict, params: dict) -> None:
    assert search(client, account, **params).status_code == 422


def test_requires_authentication(client: TestClient) -> None:
    assert client.get("/v1/communities").status_code == 401
