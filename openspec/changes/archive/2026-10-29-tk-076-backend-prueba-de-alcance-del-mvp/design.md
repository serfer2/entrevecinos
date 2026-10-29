## Context

El servicio `api` monta `docs/api` en `/docs/api` (solo lectura) y `test_owner_schema_matches_the_contract` (TK-038) ya lo lee con `contract_dir()`. Las rutas de FastAPI usan los mismos nombres de parámetro que el contrato (`{community_id}`, `{listing_id}`, `{asset_id}`, `{user_id}`).

## Decisions

- **Leer el contrato siguiendo los `$ref` de `openapi.yaml` a `paths/*.yaml`** con PyYAML (ya en `uv.lock`): sin Node ni bundle.
- **Comparar conjuntos `(método, ruta)`**, no esquemas: el objetivo es el alcance.
- **Sin `docs/api` disponible, `pytest.skip`**, como la prueba de TK-038.

## Risks / Trade-offs

- [Un parámetro renombrado en un lado] → la prueba falla y obliga a alinearlos; es el comportamiento deseado.
