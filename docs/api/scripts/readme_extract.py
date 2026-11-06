"""Regenera el extracto del contrato que incluye `readme.md` §4 (TK-077).

Lee el bundle (`dist/openapi.bundled.yaml`), conserva solo las rutas de `PATHS` y los componentes
a los que llegan sus `$ref`, y sustituye el bloque YAML entre los marcadores de `readme.md`.
Uso, desde la raíz del repositorio y tras generar el bundle:

    python3 docs/api/scripts/readme_extract.py
"""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / "docs" / "api" / "dist" / "openapi.bundled.yaml"
README = ROOT / "readme.md"
START = "<!-- openapi-extract:start -->"
END = "<!-- openapi-extract:end -->"
PATHS = ["/communities/{community_id}/listings", "/auth/register", "/auth/token"]


class LiteralDumper(yaml.SafeDumper):
    """Textos de varias líneas en bloque literal (`|`), como en el contrato."""


def _represent_str(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


LiteralDumper.add_representer(str, _represent_str)


def refs(node: object) -> set[str]:
    if isinstance(node, dict):
        found = {node["$ref"]} if isinstance(node.get("$ref"), str) else set()
        return found.union(*(refs(value) for value in node.values()))
    if isinstance(node, list):
        return set().union(*(refs(value) for value in node))
    return set()


def extract(spec: dict) -> dict:
    paths = {path: spec["paths"][path] for path in PATHS}
    # La seguridad global usa `bearerAuth` por nombre, sin `$ref`.
    components: dict[str, dict] = {"securitySchemes": spec["components"]["securitySchemes"]}
    pending = refs(paths)
    while pending:
        _, _, kind, name = pending.pop().split("/")
        if name not in components.setdefault(kind, {}):
            components[kind][name] = spec["components"][kind][name]
            pending |= refs(components[kind][name])
    operations = [op for item in paths.values() for op in item.values() if isinstance(op, dict)]
    used_tags = {tag for op in operations for tag in op.get("tags", [])}
    return {
        "openapi": spec["openapi"],
        "info": spec["info"],
        "servers": spec["servers"],
        "security": spec["security"],
        "tags": [tag for tag in spec["tags"] if tag["name"] in used_tags],
        "paths": paths,
        # Mismo orden de secciones que el contrato: el resultado no depende del orden de `pending`.
        "components": {
            kind: dict(sorted(components[kind].items()))
            for kind in spec["components"]
            if kind in components
        },
    }


def main() -> None:
    spec = yaml.safe_load(BUNDLE.read_text())
    block = yaml.dump(
        extract(spec), Dumper=LiteralDumper, sort_keys=False, allow_unicode=True, width=100
    )
    readme = README.read_text()
    before, rest = readme.split(START, 1)
    _, after = rest.split(END, 1)
    README.write_text(f"{before}{START}\n```yaml\n{block}```\n{END}{after}")


if __name__ == "__main__":
    main()
