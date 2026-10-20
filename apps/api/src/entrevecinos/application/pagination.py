from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PageRequest:
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True, slots=True)
class PageResult[T]:
    """Elementos de una página y total de elementos que cumplen el filtro."""

    items: list[T]
    total: int
