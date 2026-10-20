## Context

TK-017 expone `GET /v1/communities/{id}/memberships` y `PATCH …/memberships/{user_id}`; ambos responden `403` sin permisos.

## Goals / Non-Goals

**Goals:** revisar solicitudes con teclado y sin JavaScript; diálogo de confirmación reutilizable; la API decide los permisos.

**Non-Goals:** listado completo de miembros, bloqueo y expulsión (TK-041).

## Decisions

- **`reviewRequest` redirige** a la página con `?resultado=aprobada|rechazada|revisada|error`: el mensaje sobrevive a la revalidación (la fila desaparece) y funciona sin JavaScript.
- **`ConfirmDialog` con `<dialog>` nativo dentro del formulario:** con JavaScript, el botón abre el diálogo (`showModal()` atrapa el foco y lo devuelve al cerrar) y «Confirmar» envía el formulario; sin JavaScript, el botón envía directamente.
- **`Forbidden`** común para los `403` de páginas privadas.
- **El enlace «Gestionar comunidad»** se pinta solo para `community_admin` aprobado; la protección real es el `403` de la API.

## Risks / Trade-offs

- [Sin JavaScript no hay confirmación al rechazar] → aceptable (mejora progresiva).
