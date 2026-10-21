## Context

TK-053 responde `409` a una segunda comunidad pendiente. `GET /users/me/memberships` devuelve al creador su comunidad pendiente (membresía aprobada).

## Decisions

- **`pendingCommunityOf(memberships, userId)`:** comunidad inactiva con `created_by` igual al usuario, el mismo criterio que la API.
- **Aviso en lugar del formulario** y, por si llega igualmente (otra pestaña), mensaje propio del `409` conservando los valores.

## Risks / Trade-offs

- Ninguno relevante.
