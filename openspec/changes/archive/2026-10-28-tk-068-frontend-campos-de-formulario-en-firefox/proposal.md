## Why

HU-29: en Firefox el buscador de comunidades se sale de su panel y, al corregirlo, el campo de precio ocupa todo el ancho con el «€» desalineado. Ticket: `docs/product/tickets/EP-11-experiencia-de-usuario/HU-29-usar-los-formularios-correctamente-en-cualquier-navegador/TK-068-frontend-campos-de-formulario-en-firefox.md`.

## What Changes

- Columnas `minmax(0, …)` en el buscador de comunidades y en los filtros de anuncios.
- `w-full min-w-0` en `TextField`, `SelectField` y `TextAreaField`.
- `TextField` con `suffix`; precio con `suffix="€"` y `max-w-xs`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-design-system`: campos ajustados a su columna y precio proporcionado.

## Impact

- `apps/web` (`components/ui/`, `app/(privado)/comunidades/page.tsx`, `ListingFilters.tsx`, `ListingForm.tsx`).
