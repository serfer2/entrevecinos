## Why

Publicar un anuncio requiere categorías, el anuncio y sus imágenes, que todavía no existen en la base de datos. Ticket: `docs/product/tickets/EP-03-gestion-de-anuncios/HU-07-publicar-un-anuncio/TK-020-bd-tablas-de-anuncios-e-imagenes.md`.

## What Changes

- Enums `listing_type` y `listing_status`.
- Tablas `category` (con las diez categorías iniciales), `listing`, `media_asset` y `listing_image`, con sus restricciones e índices.
- FK `users.avatar_asset_id → media_asset.id`, pendiente desde TK-005.
- Migración `0004` reversible.

## Capabilities

### New Capabilities
- `listing-persistence`: esquema de categorías, anuncios e imágenes.

### Modified Capabilities

## Impact

- `apps/api` (modelos, migraciones y pruebas de base de datos).
