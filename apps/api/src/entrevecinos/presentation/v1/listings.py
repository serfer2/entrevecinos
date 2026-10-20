import uuid

from fastapi import APIRouter, Response, status

from entrevecinos.application.listings.delete_listing import DeleteListing
from entrevecinos.application.listings.publish_listing import PublishListing, PublishListingCommand
from entrevecinos.presentation.dependencies import (
    CategoryRepositoryDep,
    CommunityAccessDep,
    CurrentUserDep,
    ListingRepositoryDep,
    MediaRepositoryDep,
)
from entrevecinos.presentation.v1.schemas.common import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_FOUND,
    UNAUTHORIZED,
    VALIDATION_ERROR,
)
from entrevecinos.presentation.v1.schemas.listings import ListingCreateRequest, ListingResponse

router = APIRouter(tags=["Anuncios"])


@router.post(
    "/communities/{community_id}/listings",
    status_code=status.HTTP_201_CREATED,
    operation_id="createListing",
    summary="Publicar un anuncio",
    description=(
        "Crea un anuncio `active` en la comunidad. El usuario debe tener una membresía aprobada "
        "(si no, 403; con `status` si la membresía existe). Hasta 10 imágenes subidas por el "
        "usuario y no usadas en otro anuncio; la primera es la portada. Con precio y sin moneda "
        "se usa `EUR`."
    ),
    responses={**BAD_REQUEST, **UNAUTHORIZED, **FORBIDDEN, **NOT_FOUND, **VALIDATION_ERROR},
)
def create_listing(
    community_id: uuid.UUID,
    body: ListingCreateRequest,
    user: CurrentUserDep,
    access: CommunityAccessDep,
    categories: CategoryRepositoryDep,
    media: MediaRepositoryDep,
    listings: ListingRepositoryDep,
) -> ListingResponse:
    command = PublishListingCommand(
        category_id=body.category_id,
        title=body.title,
        description=body.description,
        type=body.type,
        price=body.price,
        currency=body.currency,
        image_asset_ids=tuple(body.image_asset_ids),
    )
    listing = PublishListing(access, categories, media, listings).execute(
        user, community_id, command
    )
    return ListingResponse.from_domain(listing)


@router.delete(
    "/listings/{listing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="deleteListing",
    summary="Eliminar un anuncio",
    description=(
        "Borrado lógico (`deleted_at`, `status = deleted`). Puede hacerlo el autor, un "
        "`community_admin`/`moderator` de la comunidad o un `platform_admin`. Un anuncio ya "
        "eliminado responde 404."
    ),
    responses={**UNAUTHORIZED, **FORBIDDEN, **NOT_FOUND, **VALIDATION_ERROR},
)
def delete_listing(
    listing_id: uuid.UUID,
    user: CurrentUserDep,
    access: CommunityAccessDep,
    listings: ListingRepositoryDep,
) -> Response:
    DeleteListing(access, listings).execute(user, listing_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
