## Why

HU-07: un miembro aprobado publica un anuncio con título, descripción, categoría, tipo, precio opcional y fotografías. Ticket: `docs/product/tickets/EP-03-gestion-de-anuncios/HU-07-publicar-un-anuncio/TK-022-backend-categorias-y-publicar-anuncio.md`.

## What Changes

- `GET /v1/categories` (activas, «Otros» al final).
- `POST /v1/communities/{id}/listings` con hasta 10 imágenes (la primera es la portada).
- Dominio `listings` y representación `Listing` (con `owner` e `images`) reutilizable por el resto de endpoints de anuncios.
- Contrato: `description` de anuncio limitada a 5000 caracteres y `EUR` por defecto cuando hay precio.

## Capabilities

### New Capabilities
- `listing-publication`: categorías y publicación de anuncios.

### Modified Capabilities

## Impact

- `apps/api` y `docs/api`.
