## Context

TK-032 añadió `type` y `category_id` al listado; TK-031 el buscador y `ListingSearchParams`.

## Goals / Non-Goals

**Goals:** filtros combinables que funcionan sin JavaScript; cambiar de comunidad sin perderlos.

**Non-Goals:** orden (TK-035).

## Decisions

- **`ListingSearchParams`** valida `type` contra los tipos y `category_id` como UUID (los no válidos se ignoran); `listingCriteria()` construye los parámetros para la API, la paginación, «Limpiar» y el selector.
- **`AutoSubmitSelect`** (cliente): `SelectField` que llama a `form.requestSubmit()` al cambiar; sin JavaScript se usa «Aplicar».
- **Selector de comunidad = formulario GET a `/comunidades/ir`**, un *Route Handler* que valida el id y responde `303` con un `Location` **relativo**: `request.url` lleva el host interno del contenedor (`0.0.0.0`), y una redirección absoluta a otro origen la bloquea la CSP (`form-action 'self'`).
- **«Limpiar filtros»** quita tipo y categoría y conserva la búsqueda; «Limpiar búsqueda» hace lo contrario.

## Risks / Trade-offs

- [El formulario envía `category_id=` vacío] → se ignora al leer la URL.
