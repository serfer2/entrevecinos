## Context

TK-066 aporta paleta, tipografía y logotipo.

## Decisions

- **Iconos solo donde ayudan:** lupa (búsqueda), ubicación (comunidad) y la marca.
- **Cabecera fija solo desde `sm`:** en móvil no ocupa pantalla.
- **Rejilla del listado:** 1 columna en móvil, 2 desde 420 px, 3 en `md` y 4 en `lg`.
- **Animaciones** (elevación de la tarjeta, zoom de la imagen) desactivadas con `prefers-reduced-motion`.

## Risks / Trade-offs

- [Sin pruebas visuales automáticas] → revisión manual; las pruebas existentes cubren el comportamiento.
