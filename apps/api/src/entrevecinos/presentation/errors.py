from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from entrevecinos.domain.communities.errors import (
    MembershipAlreadyExists,
    MembershipAlreadyReviewed,
    MembershipChangeRejected,
    MembershipNotApproved,
    PendingCommunityExists,
)
from entrevecinos.domain.errors import NotFoundError, PermissionDenied
from entrevecinos.domain.listings.errors import (
    CurrencyWithoutPrice,
    InvalidCategory,
    InvalidImages,
    ListingLocked,
    ListingStatusConflict,
)
from entrevecinos.domain.media.errors import EmptyImage, ImageTooLarge, UnsupportedImageType
from entrevecinos.domain.users.errors import (
    EmailAlreadyRegistered,
    EmailNotVerified,
    InvalidCredentials,
    NotAuthenticated,
    VerificationExpired,
    VerificationInvalid,
)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Solo loc, msg y type: el campo `input` repetiría los valores enviados (contraseñas incluidas).
    detail = [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder({"detail": detail}),
    )


def field_error(field: str, message: str, error_type: str) -> JSONResponse:
    """422 con el mismo formato que los errores de validación de FastAPI."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": [{"loc": ["body", field], "msg": message, "type": error_type}]},
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


async def email_not_verified_handler(request: Request, exc: EmailNotVerified) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "detail": "Tienes que validar tu correo electrónico antes de iniciar sesión.",
            "code": "email_not_verified",
        },
    )


async def verification_invalid_handler(request: Request, exc: VerificationInvalid) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "El enlace de validación no es válido.",
            "code": "verification_invalid",
        },
    )


async def verification_expired_handler(request: Request, exc: VerificationExpired) -> JSONResponse:
    # El correo permite ofrecer el reenvío sin pedirlo: quien tiene el token recibió el mensaje.
    return JSONResponse(
        status_code=status.HTTP_410_GONE,
        content={
            "detail": "El enlace de validación ha caducado.",
            "code": "verification_expired",
            "email": exc.email,
        },
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


async def membership_already_exists_handler(
    request: Request, exc: MembershipAlreadyExists
) -> JSONResponse:
    # `status` permite al frontend mostrar el estado actual (TK-017 §3.4, `MembershipConflict`).
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Ya tienes una membresía en esta comunidad.", "status": exc.status},
    )


async def pending_community_exists_handler(
    request: Request, exc: PendingCommunityExists
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Ya tienes una comunidad pendiente de aprobación."},
    )


async def permission_denied_handler(request: Request, exc: PermissionDenied) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "No tienes permisos para realizar esta acción."},
    )


async def membership_not_approved_handler(
    request: Request, exc: MembershipNotApproved
) -> JSONResponse:
    # `status` (MembershipForbidden en el contrato) permite mostrar «pendiente» o «sin acceso».
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "detail": "Tu membresía en esta comunidad no está aprobada.",
            "status": exc.status,
        },
    )


async def membership_already_reviewed_handler(
    request: Request, exc: MembershipAlreadyReviewed
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": "La solicitud ya se ha revisado."}
    )


async def membership_change_rejected_handler(
    request: Request, exc: MembershipChangeRejected
) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.detail})


async def image_too_large_handler(request: Request, exc: ImageTooLarge) -> JSONResponse:
    megabytes = exc.max_bytes // (1024 * 1024)
    return JSONResponse(
        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        content={"detail": f"La imagen supera el tamaño máximo de {megabytes} MB."},
    )


async def unsupported_image_type_handler(
    request: Request, exc: UnsupportedImageType
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        content={"detail": "Formato no permitido. Usa JPEG, PNG o WebP."},
    )


async def empty_image_handler(request: Request, exc: EmptyImage) -> JSONResponse:
    return field_error("file", "El fichero está vacío.", "empty")


async def invalid_category_handler(request: Request, exc: InvalidCategory) -> JSONResponse:
    return field_error(
        "category_id", "La categoría no existe o no está activa.", "invalid_category"
    )


async def currency_without_price_handler(
    request: Request, exc: CurrencyWithoutPrice
) -> JSONResponse:
    return field_error(
        "currency", "No se puede indicar moneda sin precio.", "currency_without_price"
    )


async def invalid_images_handler(request: Request, exc: InvalidImages) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Alguna imagen no es válida."}
    )


async def listing_status_conflict_handler(
    request: Request, exc: ListingStatusConflict
) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": exc.detail})


async def listing_locked_handler(request: Request, exc: ListingLocked) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": exc.detail})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(EmailAlreadyRegistered, email_already_registered_handler)
    app.add_exception_handler(InvalidCredentials, invalid_credentials_handler)
    app.add_exception_handler(EmailNotVerified, email_not_verified_handler)
    app.add_exception_handler(VerificationInvalid, verification_invalid_handler)
    app.add_exception_handler(VerificationExpired, verification_expired_handler)
    app.add_exception_handler(NotAuthenticated, not_authenticated_handler)
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(MembershipAlreadyExists, membership_already_exists_handler)
    app.add_exception_handler(PendingCommunityExists, pending_community_exists_handler)
    app.add_exception_handler(PermissionDenied, permission_denied_handler)
    app.add_exception_handler(ImageTooLarge, image_too_large_handler)
    app.add_exception_handler(UnsupportedImageType, unsupported_image_type_handler)
    app.add_exception_handler(EmptyImage, empty_image_handler)
    app.add_exception_handler(InvalidCategory, invalid_category_handler)
    app.add_exception_handler(CurrencyWithoutPrice, currency_without_price_handler)
    app.add_exception_handler(InvalidImages, invalid_images_handler)
    app.add_exception_handler(ListingLocked, listing_locked_handler)
    app.add_exception_handler(ListingStatusConflict, listing_status_conflict_handler)
    app.add_exception_handler(MembershipNotApproved, membership_not_approved_handler)
    app.add_exception_handler(MembershipAlreadyReviewed, membership_already_reviewed_handler)
    app.add_exception_handler(MembershipChangeRejected, membership_change_rejected_handler)
