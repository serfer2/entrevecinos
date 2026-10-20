## Context

TK-030 añadió `q` a `GET /v1/communities/{id}/listings` (mínimo 2 caracteres); TK-029 dejó `CommunityListings` y `ListingSearchParams`.

## Goals / Non-Goals

**Goals:** búsqueda compartible por URL y sin JavaScript; mensajes accesibles.

**Non-Goals:** filtros (TK-033), orden (TK-035), búsqueda mientras se escribe.

## Decisions

- **Formulario GET** hacia `/comunidades/<id>`: al buscar se vuelve a la página 1 (no se envía `page`).
- **`ListingSearchParams`** guarda `q` (válida), `qInput` (lo escrito) y `qTooShort`; `criteria()` reúne los parámetros que definen el resultado, para la API, la paginación y «Limpiar» (que en adelante conservará el resto de filtros).
- **Un carácter:** `minLength` en el navegador y, si llega por la URL, no se envía a la API: aviso junto al campo (`aria-describedby`) y listado sin filtrar.
- **Resultados en `aria-live="polite"`.**

## Risks / Trade-offs

- [Sin búsqueda mientras se escribe] → el envío explícito basta en el MVP.
