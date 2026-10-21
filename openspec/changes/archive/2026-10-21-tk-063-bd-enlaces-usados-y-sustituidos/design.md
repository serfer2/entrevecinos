## Context

Hasta ahora solo había enlaces vigentes: los demás se borraban.

## Decisions

- **Marcar en lugar de borrar (`used_at`, `superseded_at`):** la API puede explicar por qué un enlace ya no vale.
- **Índice único parcial por usuario:** como mucho un enlace vigente, también con peticiones concurrentes. `replace` ejecuta el `UPDATE` antes del `INSERT`.
- **Purga a los 30 días de la caducidad, al emitir otro enlace:** la tabla no crece sin límite y no hace falta una tarea programada.
- **`last_created_at` cuenta cualquier enlace:** el límite de un reenvío por minuto no cambia.

## Risks / Trade-offs

- [Pasados 30 días, un enlace antiguo vuelve a ser «no válido»] → aceptado: caducó hace un mes.
