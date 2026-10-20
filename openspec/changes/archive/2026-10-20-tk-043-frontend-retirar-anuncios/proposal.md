## Why

HU-17 en la interfaz: el administrador retira un anuncio inapropiado desde su detalle (y puede restaurarlo); a los miembros sin rol no se les ofrece. Ticket: `docs/product/tickets/EP-06-administracion-minima/HU-17-retirar-anuncios-problematicos/TK-043-frontend-retirar-anuncios.md`.

## What Changes

- «Retirar anuncio» (con confirmación) y «Restaurar anuncio» en `ListingActions` para gestores de la comunidad.
- Aviso «Este anuncio está retirado…» para el autor y los gestores.
- *Server Action* `moderateListing`; mensajes «Anuncio retirado.» y «Anuncio restaurado.».

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-community-admin`: retirada de anuncios.

## Impact

- `apps/web`.
