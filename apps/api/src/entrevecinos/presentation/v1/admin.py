import uuid

from fastapi import APIRouter, Response, status

from entrevecinos.application.communities.approve_communities import (
    ApproveCommunity,
    ListAllCommunities,
    RejectCommunity,
)
from entrevecinos.presentation.dependencies import CommunityRepositoryDep, CurrentUserDep
from entrevecinos.presentation.v1.pagination import Page, PageParams
from entrevecinos.presentation.v1.schemas.common import (
    CONFLICT,
    FORBIDDEN,
    NOT_FOUND,
    UNAUTHORIZED,
    VALIDATION_ERROR,
)
from entrevecinos.presentation.v1.schemas.communities import (
    AdminCommunityUpdateRequest,
    CommunityResponse,
)

router = APIRouter(prefix="/admin", tags=["Administración"])


@router.get(
    "/communities",
    operation_id="adminListCommunities",
    summary="Listar todas las comunidades",
    description=(
        "Solo `platform_admin`. Incluye las comunidades inactivas, que en el MVP son las "
        "pendientes de aprobación (`is_active=false`). De la más antigua a la más reciente."
    ),
    responses={**UNAUTHORIZED, **FORBIDDEN, **VALIDATION_ERROR},
)
def admin_list_communities(
    user: CurrentUserDep,
    communities: CommunityRepositoryDep,
    page: PageParams,
    is_active: bool | None = None,
) -> Page[CommunityResponse]:
    result = ListAllCommunities(communities).execute(user, is_active, page)
    return Page.build(result, page, [CommunityResponse.from_domain(c) for c in result.items])


@router.patch(
    "/communities/{community_id}",
    operation_id="adminUpdateCommunity",
    summary="Aprobar una comunidad",
    description=(
        "Solo `platform_admin`. En el MVP solo admite `is_active: true`, que aprueba una "
        "comunidad pendiente; desactivar (`false`) se rechaza con 422."
    ),
    responses={**UNAUTHORIZED, **FORBIDDEN, **NOT_FOUND, **VALIDATION_ERROR},
)
def admin_update_community(
    community_id: uuid.UUID,
    body: AdminCommunityUpdateRequest,
    user: CurrentUserDep,
    communities: CommunityRepositoryDep,
) -> CommunityResponse:
    return CommunityResponse.from_domain(ApproveCommunity(communities).execute(user, community_id))


@router.delete(
    "/communities/{community_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="adminRejectCommunity",
    summary="Rechazar una comunidad pendiente",
    description=(
        "Solo `platform_admin`. Elimina una comunidad pendiente de aprobación y la membresía de "
        "su creador, que podrá crear otra. Una comunidad activa responde 409."
    ),
    responses={**UNAUTHORIZED, **FORBIDDEN, **NOT_FOUND, **CONFLICT, **VALIDATION_ERROR},
)
def admin_reject_community(
    community_id: uuid.UUID, user: CurrentUserDep, communities: CommunityRepositoryDep
) -> Response:
    RejectCommunity(communities).execute(user, community_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
