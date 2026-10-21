## Why

HU-21 en la interfaz: el creador debe saber que su comunidad está pendiente y el `platform_admin` necesita una página para aprobarlas. Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-21-aprobar-las-comunidades-nuevas-antes-de-activarlas/TK-051-frontend-aprobacion-de-comunidades.md`.

## What Changes

- Tras crear una comunidad pendiente, `/inicio?comunidad-pendiente=1` con aviso de revisión; activa → su página.
- «Mis comunidades» muestra las pendientes sin enlace y con «Pendiente de aprobación».
- Página `/admin/comunidades` (solo `platform_admin`) con las pendientes y «Aprobar»; enlace en `/inicio`.

## Capabilities

### New Capabilities
- `web-platform-admin`: aprobación de comunidades desde la interfaz.

### Modified Capabilities
- `web-communities`: destino tras crear una comunidad y comunidades pendientes en «Mis comunidades».

## Impact

- `apps/web` (`features/communities`, `features/platform-admin`, `/inicio`, `/admin/comunidades`).
