import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from entrevecinos.infrastructure.settings import Settings
from entrevecinos.presentation.main import create_app


@pytest.fixture
def client() -> TestClient:
    settings = Settings(database_url="postgresql://test:test@localhost:5432/test")
    return TestClient(create_app(settings))


def test_app_metadata_matches_api_spec(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    assert schema["info"]["title"] == "API de EntreVecinos"
    assert schema["info"]["version"] == "1.0.0"


def test_app_has_no_paths(client: TestClient) -> None:
    assert client.get("/openapi.json").json()["paths"] == {}


def test_docs_are_available(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200


def test_cors_allows_configured_origin(client: TestClient) -> None:
    response = client.options(
        "/v1/",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )

    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_rejects_unknown_origin(client: TestClient) -> None:
    response = client.options(
        "/v1/",
        headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"},
    )

    assert "access-control-allow-origin" not in response.headers


def test_cors_origins_are_split_by_comma() -> None:
    settings = Settings(database_url="x", cors_origins="http://a.test, http://b.test,")

    assert settings.cors_origins_list == ["http://a.test", "http://b.test"]


def test_missing_database_url_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError, match="database_url"):
        Settings()
