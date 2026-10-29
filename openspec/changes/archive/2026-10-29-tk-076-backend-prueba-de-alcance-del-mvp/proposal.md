## Why

HU-34 AC4: tras TK-074, `x-mvp` y la API coinciden, pero nada impide que vuelvan a separarse al añadir un endpoint o cambiar el contrato. Ticket: `docs/product/tickets/EP-12-documentacion-tecnica/HU-34-distinguir-que-parte-del-modelo-de-datos-y-de-la-api-pertenece-al-mvp/TK-076-backend-prueba-de-alcance-del-mvp.md`.

## What Changes

- Prueba que compara las operaciones `(método, ruta)` de `app.openapi()` (sin `/v1`) con las `x-mvp: true` del contrato y lista las sobrantes de cada lado.
- `contract_dir()` pasa a `tests/api_helpers.py` para compartirlo.

## Capabilities

### New Capabilities

### Modified Capabilities
- `api-contract`: comprobación automática del alcance del MVP.

## Impact

- `apps/api/tests/`. Sin cambios en el código de producción ni en el contrato.
