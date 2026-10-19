from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from entrevecinos.domain.users.errors import EmailAlreadyRegistered


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


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(EmailAlreadyRegistered, email_already_registered_handler)
