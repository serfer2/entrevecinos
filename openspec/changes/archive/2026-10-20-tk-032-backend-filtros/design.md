## Context

`ListingQuery` ya tenía `type` y `category_id` (TK-028) y el repositorio separa visibilidad y criterios (TK-030).

## Goals / Non-Goals

**Goals:** filtros combinables que no saltan la regla de acceso y se reflejan en `total`.

**Non-Goals:** varios tipos a la vez (el contrato admite uno); varias comunidades a la vez.

## Decisions

- **Validación por tipos de FastAPI:** `type` fuera del enum o `category_id` que no es UUID → 422.
- **Categoría inexistente o inactiva → lista vacía**, no 422: los filtros no validan existencia.
- **Criterios en `_criteria`**, compartidos por la página y el `total`.
- `sort` y `order` siguen respondiendo 422 hasta TK-034.

## Risks / Trade-offs

- [Un solo tipo por consulta] → ampliar el contrato con una lista si negocio lo pide.
