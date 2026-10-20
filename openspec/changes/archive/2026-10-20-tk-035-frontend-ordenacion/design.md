## Context

TK-034 añadió `sort` y `order` al listado; TK-033 los filtros, `listingCriteria()` y el selector de comunidad.

## Goals / Non-Goals

**Goals:** opciones comprensibles; un orden que sobreviva a cualquier navegación del listado.

**Non-Goals:** ordenar por relevancia o cercanía.

## Decisions

- **`LISTING_ORDERS`**: `recientes` (por defecto), `antiguos`, `precio-asc`, `precio-desc`, cada uno con su etiqueta y su `sort`/`order` de la API. Un valor desconocido se trata como `recientes`.
- **URL frente a API:** `listingCriteria()` (URL, selector de comunidad, «Limpiar») lleva `orden` solo si no es el de por defecto; `listingApiQuery()` lo traduce a `sort` y `order`.
- **`GetForm`** (cliente) deshabilita los campos vacíos justo al enviar para que no aparezcan en la URL; sin JavaScript se envían y la página los ignora.

## Risks / Trade-offs

- [Un valor de `orden` desconocido se ignora en silencio] → aceptable en la interfaz (la API sí responde 422).
