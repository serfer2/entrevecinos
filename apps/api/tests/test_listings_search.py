import pytest
from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import Engine, inspect, select, text
from sqlalchemy.orm import Session

from entrevecinos.domain.listings.search import prefix_tsquery, search_words
from entrevecinos.infrastructure.db.models import ListingModel
from tests.api_helpers import create_community, join, publish_ok, register
from tests.conftest import alembic_config


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("bici rojo", "bici:* & rojo:*"),
        ("Bicicléta", "Bicicléta:*"),
        ("bici a", "bici:*"),
        ("a b", None),
        ("bici'); drop table listing;--", "bici:* & drop:* & table:* & listing:*"),
        ("a & !b", None),
        ("x:* | y", None),
        ("año_2024", "año:* & 2024:*"),
    ],
)
def test_prefix_tsquery(text: str, expected: str | None) -> None:
    assert prefix_tsquery(text) == expected


def test_search_words_ignores_single_characters() -> None:
    assert search_words("la bici de mi") == ["la", "bici", "de", "mi"]
    assert search_words("y o u") == []


@pytest.fixture
def admin(client: TestClient) -> dict:
    return register(client, "admin@example.com")


@pytest.fixture
def community(client: TestClient, admin: dict) -> dict:
    return create_community(client, admin)


@pytest.fixture
def listings(client: TestClient, admin: dict, community: dict) -> dict[str, dict]:
    created = {
        "title": publish_ok(client, admin, community["id"], title="Bicicleta de montaña"),
        "description": publish_ok(
            client,
            admin,
            community["id"],
            title="Para niños",
            description="Dos Bicicletas pequeñas",
        ),
        "truck": publish_ok(client, admin, community["id"], title="Camión de juguete"),
        "lamp": publish_ok(client, admin, community["id"], title="Lámpara roja", description="Luz"),
    }
    other = create_community(client, admin, name="Otra")
    publish_ok(client, admin, other["id"], title="Bicicleta de otra comunidad")
    return created


def search(client: TestClient, account: dict, community_id: str, q: str, **params):
    return client.get(
        f"/v1/communities/{community_id}/listings",
        params={"q": q, **params},
        headers=account["headers"],
    )


def titles(response) -> set[str]:
    return {item["title"] for item in response.json()["items"]}


@pytest.mark.db
@pytest.mark.parametrize("q", ["bicicleta", "Bicicléta", "BICI", "bici", "bicicletas"])
def test_matches_title_and_description(
    client: TestClient, admin: dict, community: dict, listings: dict, q: str
) -> None:
    response = search(client, admin, community["id"], q)

    assert response.status_code == 200
    assert titles(response) == {"Bicicleta de montaña", "Para niños"}
    assert response.json()["total"] == 2


@pytest.mark.db
def test_accents_and_all_words(
    client: TestClient, admin: dict, community: dict, listings: dict
) -> None:
    assert titles(search(client, admin, community["id"], "camion")) == {"Camión de juguete"}
    assert titles(search(client, admin, community["id"], "lampara roja")) == {"Lámpara roja"}
    assert titles(search(client, admin, community["id"], "lampara azul")) == set()


@pytest.mark.db
def test_no_results(client: TestClient, admin: dict, community: dict, listings: dict) -> None:
    body = search(client, admin, community["id"], "patinete").json()

    assert (body["items"], body["total"]) == ([], 0)


@pytest.mark.db
@pytest.mark.parametrize("q", ["", "  "])
def test_empty_query_lists_everything(
    client: TestClient, admin: dict, community: dict, listings: dict, q: str
) -> None:
    assert search(client, admin, community["id"], q).json()["total"] == 4


@pytest.mark.db
@pytest.mark.parametrize("q", ["a", " a ", "x" * 161])
def test_invalid_length(client: TestClient, admin: dict, community: dict, q: str) -> None:
    response = search(client, admin, community["id"], q)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "q"]


@pytest.mark.db
def test_minimum_message(client: TestClient, admin: dict, community: dict) -> None:
    detail = search(client, admin, community["id"], "a").json()["detail"][0]

    assert detail["msg"] == "La búsqueda debe tener al menos 2 caracteres."


@pytest.mark.db
@pytest.mark.parametrize("q", ["bici'); drop table listing;--", "a & !b", "ab:* | (", "a b"])
def test_special_characters_are_safe(
    client: TestClient, admin: dict, community: dict, listings: dict, db_session: Session, q: str
) -> None:
    assert search(client, admin, community["id"], q).status_code == 200
    assert db_session.scalar(select(ListingModel.id).limit(1)) is not None


@pytest.mark.db
def test_search_keeps_visibility_and_pagination(
    client: TestClient, admin: dict, community: dict, listings: dict
) -> None:
    member = register(client, "miembro@example.com")
    join(client, admin, member, community["id"])
    client.delete(f"/v1/listings/{listings['title']['id']}", headers=admin["headers"])

    body = search(client, member, community["id"], "bici", page_size=1).json()

    assert (body["total"], [i["title"] for i in body["items"]]) == (1, ["Para niños"])


@pytest.mark.db
def test_search_uses_the_gin_index(db_session: Session) -> None:
    db_session.execute(text("SET LOCAL enable_seqscan = off"))
    plan = "\n".join(
        db_session.scalars(
            text(
                "EXPLAIN SELECT id FROM listing "
                "WHERE search_vector @@ to_tsquery('es_unaccent', 'bici:*')"
            )
        )
    )

    assert "ix_listing_search_vector" in plan


@pytest.mark.db
def test_migration_0005_is_reversible(db_engine: Engine) -> None:
    with db_engine.begin() as connection:
        command.downgrade(alembic_config(connection), "0004")
        columns = {c["name"] for c in inspect(connection).get_columns("listing")}
        assert "search_vector" not in columns

    with db_engine.begin() as connection:
        command.upgrade(alembic_config(connection), "head")
        columns = {c["name"] for c in inspect(connection).get_columns("listing")}
        assert "search_vector" in columns
