## Context

TK-022 dejó `ListingRepository.get` (autor e imágenes); TK-021 una regla de lectura de imágenes en SQL que duplicaba la visibilidad.

## Goals / Non-Goals

**Goals:** una sola regla de visibilidad para el detalle, las imágenes y la edición; no revelar anuncios retirados a quien no puede verlos.

**Non-Goals:** correo del anunciante (TK-038).

## Decisions

- **`ListingVisibility.require_visible(user, listing)`** (aplicación): primero membresía aprobada (`require_member`: 403, con `status` si existe); después, `hidden` y `draft` solo para el autor y los gestores (`community_admin`, `moderator`, `platform_admin`) → si no, `ListingNotFound` (404).
- **Imágenes:** `GetImageUrl` busca el anuncio que usa la imagen (`MediaRepository.listing_using`) y aplica `ListingVisibility`; quien la subió la lee siempre. Se elimina `is_readable_by`.
- **Cuentas eliminadas:** `listing_with_owner()` filtra `users.deleted_at IS NULL`, así que sus anuncios dan 404 en el detalle y no aparecen en los listados.

## Risks / Trade-offs

- [403 para ajenos revela que el id existe] → el contrato lo define así; los ids son UUID aleatorios.
