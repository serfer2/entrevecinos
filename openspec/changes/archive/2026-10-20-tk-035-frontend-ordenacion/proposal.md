## Why

HU-13 en la interfaz: ordenar el listado por fecha o por precio en los dos sentidos. Ticket: `docs/product/tickets/EP-04-explorar-y-encontrar-anuncios/HU-13-ordenar-anuncios-por-fecha-o-precio/TK-035-frontend-ordenacion-de-anuncios.md`.

## What Changes

- Selector «Ordenar por» (Más recientes, Más antiguos, Precio de menor a mayor y de mayor a menor) en el formulario del listado, con un único parámetro `orden` en la URL.
- Nota «Los anuncios sin precio aparecen al final.» al ordenar por precio.
- El orden se conserva en la paginación, la búsqueda, los filtros y el cambio de comunidad.
- `GetForm`: los formularios GET no envían campos vacíos (URL limpias).

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-listings`: ordenación del listado.

## Impact

- `apps/web`.
