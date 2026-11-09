## Context

`/admin/comunidades` lista las pendientes con un formulario «Aprobar» (`approveCommunity`) y muestra el resultado desde `?resultado=` con `PENDING_COMMUNITIES_RESULT_MESSAGES`.

## Goals / Non-Goals

**Goals:** rechazar con confirmación y anclas para el enlace del correo.

**Non-Goals:** motivo del rechazo y aviso al creador.

## Decisions

- **Mensajes como funciones del nombre** (`(name) => string`) en `PENDING_COMMUNITIES_RESULT_MESSAGES`, para incluir el nombre en «Se ha rechazado la comunidad <nombre>.» sin romper los de aprobación; el nombre viaja en `?nombre=`, acotado a 120 caracteres, como en la gestión de miembros. Sin nombre, «Se ha rechazado la comunidad.».
- **Qué resultados son errores**, en `PENDING_COMMUNITIES_ERRORS` (`role="alert"` y estilo de error); el resto, `role="status"`.
- **`ConfirmDialog`** con el estilo destructivo por defecto, porque la acción no se puede deshacer.

## Risks / Trade-offs

- [Ocultar el botón no protege] → la API exige `platform_admin` (TK-112); la página ya responde 404 al resto.
