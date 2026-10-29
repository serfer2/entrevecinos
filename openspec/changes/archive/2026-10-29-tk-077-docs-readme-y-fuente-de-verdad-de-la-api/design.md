## Context

El bloque de §4 tiene tres rutas (`/communities/{community_id}/listings`, `/auth/register`, `/auth/token`) y esquemas propios, sin `operationId`, `x-mvp` ni las respuestas comunes del contrato.

## Decisions

- **Extracto generado, no escrito a mano:** `docs/api/scripts/readme_extract.py` filtra el bundle de `redocly` por esas rutas, los `components` alcanzables desde sus `$ref` y `securitySchemes`, y reescribe el bloque entre los marcadores `openapi-extract` de `readme.md`. Se descartó el decorador `filter-in` de `redocly`: deja los parámetros de ruta de las demás rutas.
- **Se mantiene un extracto** en lugar de solo un enlace, porque §4 de la plantilla del README pide incluir la especificación (asumido).
- **Sin comprobación automática del extracto:** no se acoplan las pruebas de la API al `readme.md`.

## Risks / Trade-offs

- [El extracto vuelve a quedarse atrás] → aviso «prevalece el contrato» y comando documentado para regenerarlo.
