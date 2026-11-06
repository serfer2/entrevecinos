## Context

Cientos de clases usan `emerald`, `gray`, `amber` y `red` en línea.

## Decisions

- **Redefinir las paletas en lugar de renombrarlas:** todas las páginas cambian a la vez sin tocar clases ni lógica. El nombre ya no describe el color exacto.
- **Fuentes con `next/font`:** se sirven desde el propio dominio, así que la CSP (`font-src 'self'`) no cambia.
- **Tonos 600 o superiores para texto:** contraste AA sobre blanco y sobre `gray-50`.

## Risks / Trade-offs

- [`next build` descarga las fuentes] → sin red, la compilación falla.
