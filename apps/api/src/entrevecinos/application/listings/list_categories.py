from entrevecinos.application.listings.ports import CategoryRepository
from entrevecinos.domain.listings.entities import Category


class ListCategories:
    def __init__(self, categories: CategoryRepository) -> None:
        self._categories = categories

    def execute(self) -> list[Category]:
        return self._categories.list_active()
