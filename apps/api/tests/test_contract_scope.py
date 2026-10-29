"""Las operaciones implementadas son exactamente las `x-mvp: true` del contrato (TK-076)."""

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from entrevecinos.presentation.main import create_app
from tests.api_helpers import contract_dir
from tests.conftest import make_settings

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
API_PREFIX = "/v1"


def contract_mvp_operations(docs: Path) -> set[tuple[str, str]]:
    """`(MÉTODO, ruta)` de las operaciones `x-mvp: true`, siguiendo los `$ref` de `openapi.yaml`."""
    root = yaml.safe_load((docs / "openapi.yaml").read_text())
    operations = set()
    for path, item in root["paths"].items():
        if "$ref" in item:
            item = yaml.safe_load((docs / item["$ref"]).read_text())
        for method, operation in item.items():
            if method in HTTP_METHODS and operation.get("x-mvp") is True:
                operations.add((method.upper(), path))
    return operations


def implemented_operations() -> set[tuple[str, str]]:
    """`(MÉTODO, ruta)` de la API, sin el prefijo de versión."""
    schema = TestClient(create_app(make_settings())).app.openapi()
    return {
        (method.upper(), path.removeprefix(API_PREFIX))
        for path, item in schema["paths"].items()
        for method in item
        if method in HTTP_METHODS
    }


def describe(operations: set[tuple[str, str]]) -> str:
    ordered = sorted(operations, key=lambda operation: (operation[1], operation[0]))
    return ", ".join(f"{method} {path}" for method, path in ordered)


def test_implemented_operations_match_the_mvp_contract() -> None:
    docs = contract_dir()
    if docs is None:
        pytest.skip("docs/api no está disponible (en Compose se monta en /docs/api)")

    contract = contract_mvp_operations(docs)
    implemented = implemented_operations()

    assert not implemented - contract, (
        f"Implementadas sin `x-mvp: true` en el contrato: {describe(implemented - contract)}"
    )
    assert not contract - implemented, (
        f"Marcadas `x-mvp: true` sin implementar: {describe(contract - implemented)}"
    )
