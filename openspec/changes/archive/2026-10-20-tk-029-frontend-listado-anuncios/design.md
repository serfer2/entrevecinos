## Context

TK-028 expone `GET /v1/communities/{id}/listings`. TK-016 dejó el aviso de acceso y `Pagination`; TK-023 `mediaSrc` y las etiquetas de tipo.

## Goals / Non-Goals

**Goals:** tarjetas accesibles y ligeras; no llamar al listado sin membresía aprobada; base de parámetros de URL reutilizable.

**Non-Goals:** búsqueda, filtros y orden (TK-031, TK-033, TK-035); detalle (TK-037).

## Decisions

- **`ListingSearchParams`** (`parseListingSearch`, `listingSearchQuery`, `listingSearchHref`): un único objeto con los parámetros de la URL; los tickets siguientes le añaden campos.
- **Fecha relativa hasta una semana** («hoy», «ayer», «hace N días») y corta después («12 oct.», con año si no es el actual), en la zona horaria de Madrid.
- **«Gratis»** para regalos sin precio; sin precio en el resto de tipos no se muestra nada.
- **Marcador sin imagen** con un icono neutro (SVG en línea, `aria-hidden`).

## Risks / Trade-offs

- [24 portadas = 24 redirecciones por página] → aceptable en el MVP; miniaturas post-MVP.
