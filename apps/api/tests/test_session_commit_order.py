"""La transacción se confirma antes de las tareas en segundo plano (envío de correos).

Si se confirmara después, la web leería datos sin confirmar al recargar tras una acción con correo
(p. ej. la solicitud de acceso, TK-106), porque el envío al proveedor tarda.
"""

from fastapi import BackgroundTasks, FastAPI
from fastapi.testclient import TestClient

from entrevecinos.infrastructure.db.session import get_session
from entrevecinos.presentation.dependencies import SessionDep


def test_session_commits_before_background_tasks() -> None:
    events: list[str] = []

    def fake_session():
        yield object()
        events.append("commit")

    app = FastAPI()

    @app.post("/accion")
    def action(session: SessionDep, background_tasks: BackgroundTasks) -> dict:
        background_tasks.add_task(events.append, "correo")
        return {}

    app.dependency_overrides[get_session] = fake_session

    TestClient(app).post("/accion")

    assert events == ["commit", "correo"]
