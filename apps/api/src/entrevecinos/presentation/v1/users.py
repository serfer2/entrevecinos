from fastapi import APIRouter

from entrevecinos.presentation.dependencies import CurrentUserDep
from entrevecinos.presentation.v1.schemas.common import UNAUTHORIZED
from entrevecinos.presentation.v1.schemas.users import UserResponse

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get(
    "/me",
    operation_id="getCurrentUser",
    summary="Obtener el perfil propio",
    description="Devuelve el usuario autenticado. Requiere estar autenticado.",
    responses=UNAUTHORIZED,
)
def get_me(user: CurrentUserDep) -> UserResponse:
    return UserResponse.from_domain(user)
