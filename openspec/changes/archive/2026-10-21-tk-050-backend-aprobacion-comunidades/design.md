## Context

`community.is_active` ya existe y una comunidad inactiva ya se oculta en búsquedas, detalle, accesos y anuncios; `GET /users/me/memberships` se la sigue mostrando a quien tiene la membresía aprobada (su creador). El contrato define `adminListCommunities` y `adminUpdateCommunity` sobre `is_active`, fuera del MVP.

## Decisions

- **Pendiente = inactiva:** sin columna nueva ni migración. En el MVP no se desactivan comunidades, así que `is_active: false` solo significa pendiente.
- **`adminUpdateCommunity` solo admite `is_active: true`** (`Literal[True]`, 422 con `false`), igual que `MembershipUpdate.role` se rechaza con 422.
- **Orden del listado por `created_at` e `id` ascendentes:** las pendientes más antiguas primero.
- **`ApproveCommunity` es idempotente:** aprobar una comunidad activa devuelve 200 sin cambios.
- **Pruebas:** el *helper* `create_community` aprueba la comunidad directamente en la sesión de la prueba; `create_pending_community` la deja pendiente.

## Risks / Trade-offs

- [`is_active` con doble significado si se añade la desactivación] → distinguirlos entonces (p. ej. `approved_at`).
- [Sin rechazo] → una comunidad no aprobada queda pendiente indefinidamente.
