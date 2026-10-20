## Why

HU-11 en la interfaz: buscar por palabras clave en el listado de la comunidad, ver cuántos resultados hay, un mensaje cuando no hay ninguno y poder limpiar la búsqueda. Ticket: `docs/product/tickets/EP-04-explorar-y-encontrar-anuncios/HU-11-buscar-anuncios-por-palabras-clave/TK-031-frontend-buscador-de-anuncios.md`.

## What Changes

- `ListingFilters`: formulario GET (`role="search"`) con el campo `q`, «Buscar» y «Limpiar».
- Mensajes «N resultados para "…"» y «No hay anuncios que coincidan con "…".» (distinto de la comunidad vacía).
- `ListingSearchParams` con `q`; una búsqueda de un carácter no se envía a la API y muestra el aviso.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-listings`: búsqueda de anuncios.

## Impact

- `apps/web`.
