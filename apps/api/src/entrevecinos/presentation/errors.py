from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from entrevecinos.domain.errors import NotFoundError
from entrevecinos.domain.users.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    NotAuthenticated,
)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Solo loc, msg y type: el campo `input` repetiría los valores enviados (contraseñas incluidas).
    detail = [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder({"detail": detail}),
    )


async def email_already_registered_handler(
    request: Request, exc: EmailAlreadyRegistered
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": "El correo ya está en uso."}
    )


async def invalid_credentials_handler(request: Request, exc: InvalidCredentials) -> JSONResponse:
    # Mismo mensaje para correo inexistente, contraseña incorrecta o cuenta desactivada.
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Correo o contraseña incorrectos."},
    )


async def not_authenticated_handler(request: Request, exc: NotAuthenticated) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Autenticación requerida."},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Recurso no encontrado."}
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(EmailAlreadyRegistered, email_already_registered_handler)
    app.add_exception_handler(InvalidCredentials, invalid_credentials_handler)
    app.add_exception_handler(NotAuthenticated, not_authenticated_handler)
    app.add_exception_handler(NotFoundError, not_found_handler)
