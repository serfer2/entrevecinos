import uuid

from fastapi import APIRouter

from entrevecinos.application.communities.approve_communities import (
    ApproveCommunity,
    ListAllCommunities,
)
from entrevecinos.presentation.dependencies import CommunityRepositoryDep, CurrentUserDep
from entrevecinos.presentation.v1.pagination import Page, PageParams
from entrevecinos.presentation.v1.schemas.common import (
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
