## Context

TK-042 expone `PATCH /v1/listings/{id}/status` para la moderación; TK-037 calcula `canModerate` en el servidor (membresía `community_admin`/`moderator` aprobada o `platform_admin`).

## Decisions

- **Los roles se suman** en `ListingActions`: un administrador que es el autor ve «Editar», «Eliminar» y «Retirar».
- **`moderateListing(formData)`**: al retirar vuelve a la comunidad (`?retirado=1`); al restaurar se queda en el detalle (`?restaurado=1`); `403`, `409` y otros errores vuelven al detalle con un código (`?error=moderar-permiso|moderar-estado|moderar`).
- **Retirar pide confirmación** («¿Retirar este anuncio? … Podrás restaurarlo más tarde.»); restaurar no.

## Risks / Trade-offs

- [Los anuncios retirados solo se encuentran por su URL] → un listado de retirados en la gestión lo facilitaría.
