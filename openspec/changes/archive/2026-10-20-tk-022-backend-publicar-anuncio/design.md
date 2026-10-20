## Context

TK-017 dejó `CommunityAccess`; TK-020 las tablas; TK-021 la subida de imágenes. Contrato: `categories.yaml` (`get`), `communities_community_id_listings.yaml` (`post`), `Listing`, `ListingCreate`, `ListingOwner`, `ListingImage`.

## Goals / Non-Goals

**Goals:** publicar con validación completa y en una transacción; `Decimal` de extremo a extremo; lectura de anuncios sin N+1 reutilizable.

**Non-Goals:** listado, detalle, edición, borrado y estados (tickets posteriores); gestión de categorías.

## Decisions

- **Validación de forma en el esquema** (longitudes, `Decimal` con dos decimales, moneda sin precio, imágenes repetidas → 422 por campo); **validación con datos en el caso de uso** (categoría activa → 422 en `category_id`; imágenes ajenas o ya asociadas → 400).
- **`EUR` por defecto** si hay precio sin moneda (`normalize_price` en el dominio).
- **`ListingOwner` del dominio incluye `phone` y `email`**; la respuesta solo expone `email` desde TK-038.
- **Lectura en dos consultas** (anuncios con su autor; imágenes de todos los anuncios con `IN`), compartida por `get` y los listados futuros.
- **Precio en JSON como número** (`PlainSerializer` a `float`), nunca como cadena.

## Risks / Trade-offs

- [Reutilizar una imagen en varios anuncios] → se prohíbe para simplificar permisos y borrado.
