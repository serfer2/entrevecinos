import uuid

from fastapi import APIRouter, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import RedirectResponse
from starlette.datastructures import UploadFile

from entrevecinos.application.listings.visibility import ListingVisibility
from entrevecinos.application.media.get_image_url import GetImageUrl
from entrevecinos.application.media.upload_image import UploadImage
from entrevecinos.domain.media.errors import EmptyImage, ImageTooLarge
from entrevecinos.presentation.dependencies import (
    CommunityAccessDep,
    CurrentUserDep,
    ListingRepositoryDep,
    MediaRepositoryDep,
    ObjectStorageDep,
    SettingsDep,
)
from entrevecinos.presentation.v1.schemas.common import (
    FORBIDDEN,
    NOT_FOUND,
    UNAUTHORIZED,
    VALIDATION_ERROR,
    ErrorResponse,
)
from entrevecinos.presentation.v1.schemas.media import MediaAssetResponse

router = APIRouter(prefix="/media", tags=["Media"])

# Margen para las cabeceras del multipart al comprobar `Content-Length`.
MULTIPART_OVERHEAD = 16 * 1024

UPLOAD_BODY = {
    "requestBody": {
        "required": True,
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "required": ["file"],
                    "properties": {
                        "file": {
                            "type": "string",
                            "format": "binary",
                            "description": "Imagen JPEG, PNG o WebP (tamaño máximo 5 MB).",
                        }
                    },
                }
            }
        },
    }
}


async def read_upload(request: Request, max_bytes: int) -> bytes:
    """Lee el campo `file` sin aceptar más de `max_bytes` (+1 para detectar el exceso)."""
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit():
        if int(content_length) > max_bytes + MULTIPART_OVERHEAD:
            raise ImageTooLarge(max_bytes)
    async with request.form(max_files=1, max_fields=1) as form:
        file = form.get("file")
        if not isinstance(file, UploadFile):
            raise EmptyImage
        return await file.read(max_bytes + 1)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    operation_id="uploadMedia",
    summary="Subir una imagen",
    description=(
        "Sube un fichero JPEG, PNG o WebP (máximo 5 MB) al almacenamiento de objetos y devuelve "
        "su `id`, que se usa después para asociarlo a un anuncio. El tipo se decide por el "
        "contenido del fichero, no por su nombre ni por su `Content-Type`."
    ),
    openapi_extra=UPLOAD_BODY,
    responses={
        **UNAUTHORIZED,
        **VALIDATION_ERROR,
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
    },
)
async def upload_media(
    request: Request,
    user: CurrentUserDep,
    media: MediaRepositoryDep,
    storage: ObjectStorageDep,
    settings: SettingsDep,
) -> MediaAssetResponse:
    data = await read_upload(request, settings.media_max_bytes)
    use_case = UploadImage(media, storage, settings.media_max_bytes)
    asset = await run_in_threadpool(use_case.execute, user.id, data)
    return MediaAssetResponse.from_domain(asset)


@router.get(
    "/{asset_id}",
    status_code=status.HTTP_302_FOUND,
    operation_id="getMedia",
    summary="Leer una imagen",
    description=(
        "Comprueba los permisos de lectura (la subió el usuario, o pertenece a un anuncio "
        "visible para él) y redirige a una URL prefirmada de corta duración."
    ),
    response_class=RedirectResponse,
    responses={
        302: {"description": "Redirección a la URL prefirmada de la imagen."},
        **UNAUTHORIZED,
        **FORBIDDEN,
        **NOT_FOUND,
        **VALIDATION_ERROR,
    },
)
def get_media(
    asset_id: uuid.UUID,
    user: CurrentUserDep,
    media: MediaRepositoryDep,
    storage: ObjectStorageDep,
    settings: SettingsDep,
    listings: ListingRepositoryDep,
    access: CommunityAccessDep,
) -> RedirectResponse:
    ttl = settings.media_url_ttl_seconds
    use_case = GetImageUrl(media, storage, ttl, listings, ListingVisibility(access))
    url = use_case.execute(user, asset_id)
    return RedirectResponse(
        url,
        status_code=status.HTTP_302_FOUND,
        headers={"Cache-Control": f"private, max-age={ttl - 30}"},
    )
