import uuid

from fastapi import APIRouter, status

from entrevecinos.application.communities.create_community import CreateCommunity
from entrevecinos.application.communities.get_community import GetCommunity
from entrevecinos.presentation.dependencies import CommunityRepositoryDep, CurrentUserDep
from entrevecinos.presentation.v1.schemas.common import NOT_FOUND, UNAUTHORIZED, VALIDATION_ERROR
from entrevecinos.presentation.v1.schemas.communities import (
    CommunityCreateRequest,
    CommunityResponse,
)

router = APIRouter(prefix="/communities", tags=["Comunidades"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    operation_id="createCommunity",
    summary="Crear una comunidad",
    description=(
        "El creador queda registrado como `community_admin` con membresía `approved`. "
        "Requiere estar autenticado."
    ),
    responses={**UNAUTHORIZED, **VALIDATION_ERROR},
)
def create_community(
    body: CommunityCreateRequest, user: CurrentUserDep, communities: CommunityRepositoryDep
) -> CommunityResponse:
    community = CreateCommunity(communities).execute(body.to_domain(), creator_id=user.id)
    return CommunityResponse.from_domain(community)


@router.get(
    "/{community_id}",
    operation_id="getCommunity",
    summary="Obtener una comunidad",
    description=(
        "Requiere estar autenticado. Los datos básicos son visibles para solicitar el acceso."
    ),
    responses={**UNAUTHORIZED, **NOT_FOUND, **VALIDATION_ERROR},
)
def get_community(
    community_id: uuid.UUID, user: CurrentUserDep, communities: CommunityRepositoryDep
) -> CommunityResponse:
    return CommunityResponse.from_domain(GetCommunity(communities).execute(community_id))
