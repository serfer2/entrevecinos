"""Comprueba que las capas internas no dependen de frameworks ni de capas exteriores."""

import ast
from pathlib import Path

import pytest

PACKAGE_DIR = Path(__file__).resolve().parents[1] / "src" / "entrevecinos"
FRAMEWORKS = {
    "fastapi",
    "starlette",
    "pydantic_settings",
    "uvicorn",
    "sqlalchemy",
    "alembic",
    "psycopg",
}

FORBIDDEN = {
    "domain": FRAMEWORKS
    | {
        "entrevecinos.application",
        "entrevecinos.infrastructure",
        "entrevecinos.presentation",
    },
    "application": FRAMEWORKS | {"entrevecinos.infrastructure", "entrevecinos.presentation"},
}


def imported_modules(source: str) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module)
    return modules


def violations(source: str, forbidden: set[str]) -> set[str]:
    return {
        module
        for module in imported_modules(source)
        for prefix in forbidden
        if module == prefix or module.startswith(f"{prefix}.")
    }


@pytest.mark.parametrize("layer", sorted(FORBIDDEN))
def test_layer_respects_dependency_rules(layer: str) -> None:
    found = {
        str(path.relative_to(PACKAGE_DIR)): sorted(bad)
        for path in (PACKAGE_DIR / layer).rglob("*.py")
        if (bad := violations(path.read_text(), FORBIDDEN[layer]))
    }

    assert not found, f"Imports prohibidos en '{layer}': {found}"


def test_detects_framework_import_in_domain() -> None:
    assert violations("from fastapi import APIRouter\n", FORBIDDEN["domain"]) == {"fastapi"}


def test_detects_outer_layer_import_in_application() -> None:
    source = "import entrevecinos.infrastructure.settings\n"

    assert violations(source, FORBIDDEN["application"]) == {"entrevecinos.infrastructure.settings"}
