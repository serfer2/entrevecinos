import uuid

import pytest
from fastapi.testclient import TestClient

from tests.api_helpers import category_id, create_community, join, publish_ok, register

pytestmark = pytest.mark.db


@pytest.fixture
def admin(client: TestClient) -> dict:
    return register(client, "admin@example.com")


@pytest.fixture
def community(client: TestClient, admin: dict) -> dict:
    return create_community(client, admin)


@pytest.fixture
def listings(client: TestClient, admin: dict, community: dict) -> None:
    sports = category_id(client, admin, "deporte-y-ocio")
    publish_ok(client, admin, community["id"], title="Bicicleta", type="sell", category_id=sports)
    publish_ok(client, admin, community["id"], title="Bicicleta vieja", type="free")
    publish_ok(client, admin, community["id"], title="Mesa", type="sell")
    publish_ok(
        client, admin, community["id"], title="Busco bici", type="wanted", category_id=sports
    )


def titles(client: TestClient, account: dict, community_id: str, **params) -> list[str]:
    response = client.get(
        f"/v1/communities/{community_id}/listings", params=params, headers=account["headers"]
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total"] == len(body["items"])
    return sorted(item["title"] for item in body["items"])


def test_filter_by_type(client: TestClient, admin: dict, community: dict, listings: None) -> None:
    assert titles(client, admin, community["id"], type="sell") == ["Bicicleta", "Mesa"]
    assert titles(client, admin, community["id"], type="free") == ["Bicicleta vieja"]
    assert titles(client, admin, community["id"], type="offer_service") == []


def test_filter_by_category(
    client: TestClient, admin: dict, community: dict, listings: None
) -> None:
    sports = category_id(client, admin, "deporte-y-ocio")

    assert titles(client, admin, community["id"], category_id=sports) == ["Bicicleta", "Busco bici"]
    assert titles(client, admin, community["id"], category_id=str(uuid.uuid4())) == []


def test_filters_combine_with_search(
    client: TestClient, admin: dict, community: dict, listings: None
) -> None:
    sports = category_id(client, admin, "deporte-y-ocio")

    assert titles(client, admin, community["id"], q="bici", type="sell") == ["Bicicleta"]
    assert titles(client, admin, community["id"], q="bici", category_id=sports, type="wanted") == [
        "Busco bici"
    ]


@pytest.mark.parametrize("params", [{"type": "foo"}, {"category_id": "no-es-uuid"}])
def test_invalid_filters(client: TestClient, admin: dict, community: dict, params: dict) -> None:
    response = client.get(
        f"/v1/communities/{community['id']}/listings", params=params, headers=admin["headers"]
    )

    assert response.status_code == 422


def test_each_community_has_its_own_listings(
    client: TestClient, admin: dict, community: dict, listings: None
) -> None:
    member = register(client, "miembro@example.com")
    join(client, admin, member, community["id"])
    other = create_community(client, admin, name="Otra")
    join(client, admin, member, other["id"])
    publish_ok(client, admin, other["id"], title="Sofá", type="sell")

    assert titles(client, member, other["id"], type="sell") == ["Sofá"]
    assert "Sofá" not in titles(client, member, community["id"], type="sell")


def test_filters_do_not_bypass_access(client: TestClient, community: dict) -> None:
    outsider = register(client, "ajeno@example.com")

    response = client.get(
        f"/v1/communities/{community['id']}/listings",
        params={"type": "sell"},
        headers=outsider["headers"],
    )
    assert response.status_code == 403
