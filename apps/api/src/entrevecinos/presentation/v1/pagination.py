from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel

from entrevecinos.application.pagination import PageRequest, PageResult


def page_params(
    page: Annotated[int, Query(ge=1, description="Número de página (empieza en 1).")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Elementos por página.")] = 20,
) -> PageRequest:
    return PageRequest(page=page, page_size=page_size)


PageParams = Annotated[PageRequest, Depends(page_params)]


class Page[T](BaseModel):
    """Respuesta paginada común (`PageMeta` + `items`)."""

    items: list[T]
    page: int
    page_size: int
    total: int

    @classmethod
    def build[S](cls, result: PageResult[S], request: PageRequest, items: list[T]) -> "Page[T]":
        return cls(items=items, page=request.page, page_size=request.page_size, total=result.total)
