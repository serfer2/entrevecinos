## Context

TK-040 añadió el bloqueo (`PATCH … status: blocked|approved`) y la expulsión (`DELETE`); TK-018 dejó la gestión de solicitudes, `ConfirmDialog` y `Forbidden`.

## Decisions

- **Acciones por fila** (`rowActions`, función pura): miembro → «Bloquear», «Expulsar»; bloqueado → «Desbloquear», «Expulsar»; rechazado → «Expulsar»; pendiente → «Ir a solicitudes»; administradores y yo mismo → ninguna.
- **`manageMember`** redirige a la página con `resultado` y `nombre` («Mario ha sido bloqueado.») o con un **código** de conflicto (`error=ultimo-admin`…), que la página traduce: nunca se pone texto arbitrario de la API en la URL.
- **Filtro por estado** con enlaces (`?estado=pendiente|miembro|bloqueado|rechazado`) y `aria-current`.
- **403 → `Forbidden`** igual que en las solicitudes.

## Risks / Trade-offs

- [Sin motivo del bloqueo] → un campo de motivo ayudaría a la auditoría (post-MVP).
