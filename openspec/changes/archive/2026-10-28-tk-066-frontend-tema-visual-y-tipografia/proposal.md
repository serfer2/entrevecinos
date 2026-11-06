## Why

HU-28: la interfaz usa los colores y la fuente por defecto de Tailwind; es correcta pero genérica, sin identidad propia. Ticket: `docs/product/tickets/EP-11-experiencia-de-usuario/HU-28-usar-una-interfaz-sencilla-clara-y-con-identidad-propia/TK-066-frontend-tema-visual-y-tipografia.md`.

## What Changes

- `globals.css`: paletas `emerald` (verde musgo), `gray` (piedra y tierra), `amber` (ocre) y `red` (terracota) redefinidas en `@theme`; estilos base (fondo, títulos, enlaces, foco y selección).
- Figtree (texto) y Fraunces (títulos) autoalojadas con `next/font`.
- Logotipo `BrandMark`.

## Capabilities

### New Capabilities
- `web-design-system`: identidad visual, tipografía y logotipo.

### Modified Capabilities

## Impact

- `apps/web` (`src/styles/globals.css`, `src/app/layout.tsx`, `src/components/brand/`).
