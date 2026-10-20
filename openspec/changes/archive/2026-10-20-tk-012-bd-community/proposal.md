## Why

Comunidades y membresías son la base del control de acceso (solo los miembros aprobados ven y publican anuncios). Ticket: `docs/product/tickets/EP-02-comunidades/HU-04-crear-una-comunidad/TK-012-bd-tablas-community-y-community-membership.md`.

## What Changes

- Enums `membership_role` y `membership_status`.
- Tablas `community` y `community_membership` (nombres en singular; `users` es la excepción).
- Migración `0002_create_community` reversible y modelos ORM.

## Capabilities

### New Capabilities
- `community-persistence`: esquema de comunidades y membresías.

### Modified Capabilities

## Impact

- `apps/api` (modelos, migraciones y pruebas de base de datos).
