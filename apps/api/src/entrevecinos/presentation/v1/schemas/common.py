from typing import Any

from pydantic import BaseModel


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
UNAUTHORIZED: dict[int | str, dict[str, Any]] = {401: {"model": ErrorResponse}}
VALIDATION_ERROR: dict[int | str, dict[str, Any]] = {422: {"model": ValidationErrorResponse}}
