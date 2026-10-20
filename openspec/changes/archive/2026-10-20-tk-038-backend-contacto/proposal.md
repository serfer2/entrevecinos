## Why

HU-15: el canal de contacto del MVP es el teléfono y/o el correo del anunciante, solo para miembros aprobados; el contrato de `ListingOwner` no incluía el correo. Ticket: `docs/product/tickets/EP-05-detalle-y-contacto/HU-15-contactar-con-el-anunciante/TK-038-backend-datos-de-contacto-del-anunciante.md`.

## What Changes

- Contrato: `ListingOwner.email` (obligatorio, `format: email`); *bundle* regenerado y changelog en `docs/api/README.md`.
- `ListingOwnerResponse` con `email`.
- Pruebas de que los datos de contacto nunca llegan a no miembros y de que el esquema coincide con el contrato (`docs/api` montado en el contenedor `api`).

## Capabilities

### New Capabilities

### Modified Capabilities
- `listing-detail`: datos de contacto del anunciante.

## Impact

- `docs/api`, `apps/api`, `infra/docker-compose.yml` (montaje de solo lectura del contrato).
