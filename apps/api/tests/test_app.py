import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from entrevecinos.infrastructure.settings import Settings
from entrevecinos.presentation.main import create_app
from tests.conftest import make_settings


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(make_settings()))


def test_app_metadata_matches_api_spec(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    assert schema["info"]["title"] == "API de EntreVecinos"
    assert schema["info"]["version"] == "1.0.0"


def test_routes_are_versioned(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert paths
    assert all(path.startswith("/v1/") for path in paths)


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
    settings = make_settings(cors_origins="http://a.test, http://b.test,")

    assert settings.cors_origins_list == ["http://a.test", "http://b.test"]


def test_missing_database_url_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError, match="database_url"):
        Settings(jwt_secret="x" * 32)


def test_missing_jwt_secret_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(ValidationError, match="jwt_secret"):
        Settings(database_url="postgresql+psycopg://x:y@z/db")


def test_short_jwt_secret_fails() -> None:
    with pytest.raises(ValidationError, match="jwt_secret"):
        make_settings(jwt_secret="too-short")


def test_permission_errors_map_to_403() -> None:
    from fastapi.testclient import TestClient

    from entrevecinos.domain.communities.entities import MembershipStatus
    from entrevecinos.domain.communities.errors import MembershipNotApproved
    from entrevecinos.domain.errors import PermissionDenied
    from entrevecinos.presentation.main import create_app
    from tests.conftest import make_settings

    app = create_app(make_settings())

    @app.get("/denied")
    def denied() -> None:
        raise PermissionDenied

    @app.get("/pending")
    def pending() -> None:
        raise MembershipNotApproved(MembershipStatus.PENDING)

    client = TestClient(app)
    assert client.get("/denied").json() == {
        "detail": "No tienes permisos para realizar esta acción."
    }
    response = client.get("/pending")
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Tu membresía en esta comunidad no está aprobada.",
        "status": "pending",
    }
