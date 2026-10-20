import uuid

from sqlalchemy import case, select
from sqlalchemy.orm import Session

from entrevecinos.domain.listings.entities import Category
from entrevecinos.infrastructure.db.models import CategoryModel

# Categoría comodín que se muestra siempre en último lugar.
CATCH_ALL_SLUG = "otros"


class SqlAlchemyCategoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_active(self) -> list[Category]:
        models = self._session.scalars(
            select(CategoryModel)
            .where(CategoryModel.is_active.is_(True))
            .order_by(case((CategoryModel.slug == CATCH_ALL_SLUG, 1), else_=0), CategoryModel.name)
        )
        return [Category(id=m.id, name=m.name, slug=m.slug, is_active=m.is_active) for m in models]

    def is_active(self, category_id: uuid.UUID) -> bool:
        model = self._session.get(CategoryModel, category_id)
        return model is not None and model.is_active
