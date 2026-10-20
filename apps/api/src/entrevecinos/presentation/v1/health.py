from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from entrevecinos.presentation.dependencies import SessionDep

router = APIRouter(tags=["Sistema"])


class HealthResponse(BaseModel):
    """Esquema `Health` del contrato."""

    status: Literal["ok"]


@router.get(
    "/health",
    response_model=HealthResponse,
    operation_id="getHealth",
    summary="Comprobar el estado del servicio",
    description=(
        "Endpoint público para sondas de disponibilidad (Docker healthcheck, balanceador). "
        "Comprueba la conexión con la base de datos: si falla, responde 503."
    ),
    responses={503: {"description": "Servicio no disponible (sin conexión con la base de datos)."}},
)
def get_health(session: SessionDep) -> HealthResponse | JSONResponse:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"detail": "Servicio no disponible."})
    return HealthResponse(status="ok")
