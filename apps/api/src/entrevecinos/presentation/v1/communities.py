import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from entrevecinos.application.communities.create_community import CreateCommunity
from entrevecinos.application.communities.get_community import GetCommunity
from entrevecinos.application.communities.request_membership import RequestMembership
from entrevecinos.application.communities.search_communities import SearchCommunities
from entrevecinos.domain.communities.entities import CommunitySearch
from entrevecinos.presentation.dependencies import (
    CommunityRepositoryDep,
    CurrentUserDep,
    MembershipRepositoryDep,
)
from entrevecinos.presentation.v1.pagination import Page, PageParams
from entrevecinos.presentation.v1.schemas.common import NOT_FOUND, UNAUTHORIZED, VALIDATION_ERROR
from entrevecinos.presentation.v1.schemas.communities import (
    CommunityCreateRequest,
    CommunityResponse,
    MembershipErrorResponse,
    MembershipResponse,
)


def _search_term(value: str | None) -> str | None:
    return value.strip() or None if value is not None else None


router = APIRouter(prefix="/communities", tags=["Comunidades"])


@router.get(
    "",
    operation_id="listCommunities",
    summary="Buscar comunidades",
    description=(
        "Explora las comunidades activas para solicitar el acceso. `q` busca en el nombre y la "
        "descripción, `city` en la ciudad y `postal_code` por prefijo, sin distinguir mayúsculas "
        "ni tildes. Requiere estar autenticado."
    ),
    responses={**UNAUTHORIZED, **VALIDATION_ERROR},
)
def list_communities(
    user: CurrentUserDep,
    communities: CommunityRepositoryDep,
    page: PageParams,
    q: Annotated[str | None, Query(max_length=160)] = None,
    city: Annotated[str | None, Query(max_length=120)] = None,
    postal_code: Annotated[str | None, Query(max_length=16)] = None,
) -> Page[CommunityResponse]:
    filters = CommunitySearch(
        text=_search_term(q), city=_search_term(city), postal_code=_search_term(postal_code)
    )
    result = SearchCommunities(communities).execute(filters, page)
    return Page.build(result, page, [CommunityResponse.from_domain(c) for c in result.items])


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


@router.post(
    "/{community_id}/memberships",
    status_code=status.HTTP_201_CREATED,
    operation_id="requestMembership",
    summary="Solicitar el acceso a una comunidad",
    description=(
        "Crea una membresía `pending` con rol `member` para el usuario autenticado; un "
        "administrador debe aprobarla. Sin cuerpo de petición. Si ya existe una membresía en "
        "cualquier estado responde 409 con su `status`."
    ),
    responses={
        **UNAUTHORIZED,
        **NOT_FOUND,
        **VALIDATION_ERROR,
        409: {"model": MembershipErrorResponse},
    },
)
def request_membership(
    community_id: uuid.UUID,
    user: CurrentUserDep,
    communities: CommunityRepositoryDep,
    memberships: MembershipRepositoryDep,
) -> MembershipResponse:
    detail = RequestMembership(communities, memberships).execute(community_id, user.id)
    return MembershipResponse.from_domain(detail)
