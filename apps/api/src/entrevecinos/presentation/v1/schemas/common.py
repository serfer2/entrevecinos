from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, Field, StringConstraints


class ErrorResponse(BaseModel):
    detail: str


class ValidationErrorItem(BaseModel):
    loc: list[str | int]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: list[ValidationErrorItem]


# Respuestas de error documentadas en OpenAPI, reutilizables por los routers.
CONFLICT: dict[int | str, dict[str, Any]] = {409: {"model": ErrorResponse}}
FORBIDDEN: dict[int | str, dict[str, Any]] = {403: {"model": ErrorResponse}}
NOT_FOUND: dict[int | str, dict[str, Any]] = {404: {"model": ErrorResponse}}
UNAUTHORIZED: dict[int | str, dict[str, Any]] = {401: {"model": ErrorResponse}}
VALIDATION_ERROR: dict[int | str, dict[str, Any]] = {422: {"model": ValidationErrorResponse}}


def _blank_to_none(value: object) -> object:
    if isinstance(value, str):
        return value.strip() or None
    return value


def RequiredText(max_length: int) -> Any:  # noqa: N802 (alias de tipo)
    """Texto obligatorio: se recortan los espacios y no puede quedar vacío."""
    return Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=max_length)
    ]


def OptionalText(max_length: int) -> Any:  # noqa: N802 (alias de tipo)
    """Texto opcional: se recortan los espacios y `""` equivale a `null`."""
    return Annotated[
        Annotated[str, StringConstraints(max_length=max_length)] | None,
        BeforeValidator(_blank_to_none),
        Field(default=None),
    ]
