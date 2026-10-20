## Context

TK-022 dejó `ListingLoader` y `listing_with_owner()`; TK-017 `CommunityAccess`.

## Goals / Non-Goals

**Goals:** listado paginado estable, filtro de visibilidad centralizado, número fijo de consultas.

**Non-Goals:** búsqueda, filtros y orden (tickets siguientes).

## Decisions

- **`ListingQuery`** con todos los criterios del contrato desde ya (texto, tipo, categoría, orden); el repositorio aplica los que estén informados.
- **Filtro de visibilidad único** (`_visible_in_community`): comunidad, `status IN (active, reserved)` y no eliminado. Lo comparten la página y el `total`; TK-040 le añadirá la membresía del autor.
- **Desempate por `id DESC`** para que la paginación no repita ni pierda elementos.
- **Parámetros aún no implementados → 422** con una dependencia `reject_unsupported` en lugar de ignorarlos en silencio.

## Risks / Trade-offs

- [Se devuelve el `Listing` completo] → coherente con el contrato; un esquema resumido si pesa.
