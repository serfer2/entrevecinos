from fastapi import APIRouter

from entrevecinos.application.listings.list_categories import ListCategories
from entrevecinos.presentation.dependencies import CategoryRepositoryDep, CurrentUserDep
from entrevecinos.presentation.v1.schemas.common import UNAUTHORIZED
from entrevecinos.presentation.v1.schemas.listings import CategoriesResponse, CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categorías"])


@router.get(
    "",
    operation_id="listCategories",
    summary="Listar categorías",
    description=(
        "Devuelve las categorías activas, ordenadas por nombre y con «Otros» al final. "
        "Requiere estar autenticado."
    ),
    responses=UNAUTHORIZED,
)
def list_categories(user: CurrentUserDep, categories: CategoryRepositoryDep) -> CategoriesResponse:
    items = ListCategories(categories).execute()
    return CategoriesResponse(items=[CategoryResponse.from_domain(c) for c in items])
