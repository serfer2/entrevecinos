## Context

En Firefox el ancho natural de un `<input>` es mayor que en Chrome, y una columna `fr` no baja de él.

## Decisions

- **`minmax(0, …)` en las rejillas y `min-w-0` en los campos:** el campo se ajusta a su columna en cualquier navegador.
- **`suffix` decorativo (`aria-hidden`):** la ayuda del campo ya explica la unidad; el campo reserva `pr-9`.
- **Precio de 20 rem como máximo:** deja sitio a la ayuda sin partirla (asumido).

## Risks / Trade-offs

- [Comprobación manual en Firefox] → sin pruebas automáticas de maquetación.
