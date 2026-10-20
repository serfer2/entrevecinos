## Why

HU-12 en la interfaz: filtrar por tipo (y categoría), cambiar entre mis comunidades y combinar los filtros con la palabra clave. Ticket: `docs/product/tickets/EP-04-explorar-y-encontrar-anuncios/HU-12-filtrar-anuncios-por-comunidad-y-tipo/TK-033-frontend-filtros-y-selector-de-comunidad.md`.

## What Changes

- Desplegables «Tipo» y «Categoría» en el mismo formulario GET que la búsqueda («Aplicar»; con JavaScript se aplican al cambiar).
- Indicador de filtros activos, «Limpiar filtros» y «No hay anuncios con estos filtros.».
- `CommunitySwitcher` (si soy miembro aprobado de dos o más comunidades) y ruta `/comunidades/ir` que conserva la búsqueda y los filtros.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-listings`: filtros y cambio de comunidad.

## Impact

- `apps/web`.
