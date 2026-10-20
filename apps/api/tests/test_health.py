import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError


@pytest.mark.db
def test_health_is_public_and_checks_the_database(client: TestClient) -> None:
    response = client.get("/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_without_database_is_503() -> None:
    from entrevecinos.infrastructure.db.session import get_session
    from entrevecinos.presentation.main import create_app
    from tests.conftest import make_settings

    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise OperationalError("SELECT 1", {}, Exception("sin conexión"))

    app = create_app(make_settings())
    app.dependency_overrides[get_session] = lambda: BrokenSession()

    response = TestClient(app).get("/v1/health")

    assert response.status_code == 503
    assert response.json() == {"detail": "Servicio no disponible."}
