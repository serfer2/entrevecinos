## Context

En el MVP, una comunidad inactiva es una comunidad pendiente de aprobación (TK-050), y su creador queda en `community.created_by`.

## Decisions

- **Comprobación en `CreateCommunity` + índice único parcial:** el caso de uso da el error de negocio y el índice cierra la carrera entre peticiones simultáneas; `add` usa un *savepoint* y traduce el `IntegrityError` del índice en `PendingCommunityExists`.
- **El `platform_admin` no queda limitado:** sus comunidades nacen activas (TK-052).
- **«Pendiente» por `created_by`**, no por la membresía: no depende de que el creador siga siendo miembro.

## Risks / Trade-offs

- [Sin rechazo ni retirada] → si nadie aprueba la comunidad, el usuario no puede crear otra.
