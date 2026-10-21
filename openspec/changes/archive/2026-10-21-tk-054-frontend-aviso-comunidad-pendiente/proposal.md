## Why

HU-23 en la interfaz: avisar de que ya hay una comunidad pendiente antes de rellenar el formulario. Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-23-tener-una-sola-comunidad-pendiente-de-aprobacion-a-la-vez/TK-054-frontend-aviso-de-comunidad-pendiente.md`.

## What Changes

- `/comunidades/nueva` muestra un aviso con el nombre de la comunidad pendiente en lugar del formulario.
- `createCommunity` traduce el `409` en «Ya tienes una comunidad pendiente de aprobación.».

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-communities`: aviso de comunidad pendiente al crear.

## Impact

- `apps/web` (`features/communities`, `/comunidades/nueva`).
