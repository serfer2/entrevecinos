## Why

HU-28: con el tema de TK-066 la estructura sigue siendo la de un prototipo (formularios sin superficie, tarjetas planas, filtros dispersos, páginas públicas sin marca). Ticket: `docs/product/tickets/EP-11-experiencia-de-usuario/HU-28-usar-una-interfaz-sencilla-clara-y-con-identidad-propia/TK-067-frontend-rediseno-de-paginas-y-componentes.md`.

## What Changes

- `AuthShell` para inicio de sesión, registro y error de validación del correo.
- Cabecera privada con logotipo (fija desde `sm`) y pie de página.
- `ListingCard` con tipo y «Reservado» sobre la imagen y precio destacado.
- Búsqueda, filtros y orden en un panel; listas y formularios sobre superficies blancas.
- Estado vacío, cabecera de la comunidad con ubicación y detalle con etiquetas, galería y anunciante en paneles.

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-design-system`: estructura de las páginas, tarjetas, panel de búsqueda y adaptación a móvil.
- `web-communities`: cabecera privada con logotipo y pie.

## Impact

- `apps/web` (páginas de `app/`, `components/ui/`, `features/*/components/`). Sin cambios de funcionalidad ni de textos de negocio.
