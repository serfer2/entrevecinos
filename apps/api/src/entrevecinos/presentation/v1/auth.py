from typing import Annotated

from fastapi import APIRouter, Depends, status

from entrevecinos.application.users.authenticate_user import AuthenticateUser, LoginCommand
from entrevecinos.application.users.register_user import RegisterUser, RegisterUserCommand
from entrevecinos.presentation.dependencies import get_authenticate_user, get_register_user
from entrevecinos.presentation.v1.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from entrevecinos.presentation.v1.schemas.common import CONFLICT, UNAUTHORIZED, VALIDATION_ERROR
from entrevecinos.presentation.v1.schemas.users import UserResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    operation_id="registerUser",
    summary="Registrar una cuenta",
    description="Crea una cuenta con rol `user` y devuelve un token JWT para iniciar la sesión.",
    responses={**CONFLICT, **VALIDATION_ERROR},
)
def register(
    body: RegisterRequest, register_user: Annotated[RegisterUser, Depends(get_register_user)]
) -> AuthResponse:
    user, token = register_user.execute(
        RegisterUserCommand(
            email=body.email, password=body.password, full_name=body.full_name, phone=body.phone
        )
    )
    return AuthResponse(
        access_token=token.token, expires_in=token.expires_in, user=UserResponse.from_domain(user)
    )


@router.post(
    "/token",
    operation_id="loginUser",
    summary="Iniciar sesión",
    description="Valida las credenciales y emite un token JWT. Acceso público.",
    responses={**UNAUTHORIZED, **VALIDATION_ERROR},
)
def login(
    body: LoginRequest,
    authenticate_user: Annotated[AuthenticateUser, Depends(get_authenticate_user)],
) -> AuthResponse:
    user, token = authenticate_user.execute(LoginCommand(email=body.email, password=body.password))
    return AuthResponse(
        access_token=token.token, expires_in=token.expires_in, user=UserResponse.from_domain(user)
    )
