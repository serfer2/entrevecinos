import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.orm import Session

from entrevecinos.infrastructure.db.models import ListingModel
from tests.api_helpers import create_community, publish_ok, register

pytestmark = pytest.mark.db

BASE = datetime(2026, 10, 1, tzinfo=UTC)


@pytest.fixture
def admin(client: TestClient) -> dict:
    return register(client, "admin@example.com")


@pytest.fixture
def community(client: TestClient, admin: dict) -> dict:
    return create_community(client, admin)


@pytest.fixture
def listings(client: TestClient, admin: dict, community: dict, db_session: Session) -> None:
    """Título → (precio, días desde BASE). Dos sin precio y dos con la misma fecha."""
    data = {
        "barato": (5, 1),
        "caro": (100, 2),
        "medio": (40, 3),
        "gratis": (None, 4),
        "nada": (None, 4),
    }
    for title, (price, days) in data.items():
        created = publish_ok(client, admin, community["id"], title=title, price=price)
        db_session.execute(
            update(ListingModel)
            .where(ListingModel.id == uuid.UUID(created["id"]))
            .values(published_at=BASE + timedelta(days=days))
        )


def order(client: TestClient, admin: dict, community: dict, **params) -> list[str]:
    response = client.get(
        f"/v1/communities/{community['id']}/listings", params=params, headers=admin["headers"]
    )
    assert response.status_code == 200, response.text
    return [item["title"] for item in response.json()["items"]]


def test_default_is_newest_first(client, admin, community, listings) -> None:
    titles = order(client, admin, community)

    assert titles[2:] == ["medio", "caro", "barato"]
    assert set(titles[:2]) == {"gratis", "nada"}
    assert order(client, admin, community, sort="published_at", order="desc") == titles


def test_oldest_first(client, admin, community, listings) -> None:
    titles = order(client, admin, community, sort="published_at", order="asc")

    assert titles[:3] == ["barato", "caro", "medio"]
    assert titles == list(reversed(order(client, admin, community)))


def test_by_price_with_unpriced_last(client, admin, community, listings) -> None:
    ascending = order(client, admin, community, sort="price", order="asc")
    descending = order(client, admin, community, sort="price", order="desc")

    assert ascending[:3] == ["barato", "medio", "caro"]
    assert descending[:3] == ["caro", "medio", "barato"]
    assert set(ascending[3:]) == set(descending[3:]) == {"gratis", "nada"}
    # Sin `order`, el contrato usa `desc` también con el precio.
    assert order(client, admin, community, sort="price") == descending


def test_tie_breaker_is_stable_between_pages(client, admin, community, listings) -> None:
    full = order(client, admin, community, sort="price", order="asc")
    paged = [
        title
        for page in (1, 2, 3)
        for title in order(
            client, admin, community, sort="price", order="asc", page=page, page_size=2
        )
    ]

    assert paged == full


def test_sort_combines_with_filters(client, admin, community, listings) -> None:
    assert order(client, admin, community, sort="price", order="asc", q="medio") == ["medio"]
