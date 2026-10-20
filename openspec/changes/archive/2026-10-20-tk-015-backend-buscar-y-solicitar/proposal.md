## Why

HU-05: buscar comunidades, solicitar el acceso sin duplicar solicitudes y conocer su estado. Ticket: `docs/product/tickets/EP-02-comunidades/HU-05-seleccionar-una-comunidad-y-solicitar-el-acceso/TK-015-backend-buscar-comunidades-y-solicitar-acceso.md`.

## What Changes

- Paginación común (`PageRequest`/`PageResult` en aplicación; `PageParams`/`Page[T]` en presentación).
- Migración `0003`: extensión `unaccent` y función inmutable `f_unaccent(text)`.
- `GET /v1/communities` (búsqueda sin mayúsculas ni tildes), `POST /v1/communities/{id}/memberships` y `GET /v1/users/me/memberships`.
- `409` de solicitud duplicada con el campo `status`.

## Capabilities

### New Capabilities
- `api-pagination`: parámetros y respuesta comunes de los listados.
- `community-access-requests`: búsqueda de comunidades y solicitudes de acceso.

### Modified Capabilities

## Impact

- `apps/api` (migración, dominio, aplicación, infraestructura, presentación y pruebas).
