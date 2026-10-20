## Context

TK-026 expone `DELETE /v1/listings/{id}`; TK-018 dejó `ConfirmDialog`; TK-037 `ListingActions`.

## Goals / Non-Goals

**Goals:** confirmación accesible; la comunidad de destino sale del anuncio leído en el servidor.

**Non-Goals:** retirada por administradores (TK-043; en la interfaz el administrador retira, no elimina).

## Decisions

- **`deleteListing(formData)`** lee el anuncio (`GET`) para saber su comunidad y después envía `DELETE`. Los resultados se comunican por la URL para que funcionen sin JavaScript y tras la redirección:
  - `204` → `/comunidades/<id>?eliminado=1` («Anuncio eliminado.»).
  - `404` (al leer o al borrar) → la comunidad si se conoce, si no `/inicio`, con `?no-disponible=1` («Este anuncio ya no estaba disponible.»).
  - `403` → `/anuncios/<id>?error=eliminar-permiso`; red o `5xx` → `?error=eliminar`.
- **Diálogo:** «¿Eliminar este anuncio?», «Dejará de verse en la comunidad. Esta acción no se puede deshacer.», foco inicial en «Cancelar».

## Risks / Trade-offs

- [Sin deshacer] → el texto del diálogo lo advierte.
