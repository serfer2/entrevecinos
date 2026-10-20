## Why

HU-09b en la interfaz: el autor marca su anuncio como reservado o finalizado y puede quitar la reserva; nadie más tiene esas opciones. Ticket: `docs/product/tickets/EP-03-gestion-de-anuncios/HU-09b-marcar-mi-anuncio-como-reservado-o-finalizado/TK-045-frontend-reservar-y-finalizar-anuncio.md`.

## What Changes

- «Marcar como reservado», «Quitar reserva» y «Marcar como finalizado» (con confirmación) en `ListingActions`, solo para el autor.
- *Server Action* `changeListingStatus` con mensajes de resultado en el detalle.
- Etiqueta «Finalizado» y aviso «Este anuncio está finalizado.» en el detalle; sin «Editar» en anuncios finalizados.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-listings`: estados reservado y finalizado.

## Impact

- `apps/web`.
