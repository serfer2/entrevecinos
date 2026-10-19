from fastapi import APIRouter

from entrevecinos.application.users.update_profile import UNSET, ProfileChanges, UpdateProfile
from entrevecinos.presentation.dependencies import CurrentUserDep, UserRepositoryDep
from entrevecinos.presentation.v1.schemas.common import UNAUTHORIZED, VALIDATION_ERROR
from entrevecinos.presentation.v1.schemas.users import UserResponse, UserUpdateRequest

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


@router.patch(
    "/me",
    operation_id="updateCurrentUser",
    summary="Actualizar el perfil propio",
    description=(
        'Actualización parcial del nombre y el teléfono (`null` o `""` borra el teléfono). '
        "Requiere estar autenticado. **Pendiente:** `avatar_asset_id`, `password` y "
        "`current_password` del contrato `UserUpdate` todavía no están implementados y se "
        "rechazan con 422."
    ),
    responses={**UNAUTHORIZED, **VALIDATION_ERROR},
)
def update_me(
    body: UserUpdateRequest, user: CurrentUserDep, users: UserRepositoryDep
) -> UserResponse:
    sent = body.model_fields_set
    changes = ProfileChanges(
        full_name=body.full_name if "full_name" in sent else UNSET,
        phone=body.phone if "phone" in sent else UNSET,
    )
    return UserResponse.from_domain(UpdateProfile(users).execute(user.id, changes))
