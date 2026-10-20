## Context

`ListingQuery` ya tenía `sort` y `order` (TK-028); el repositorio ordenaba siempre por `published_at DESC, id DESC`.

## Goals / Non-Goals

**Goals:** cuatro órdenes con desempate estable; anuncios sin precio siempre al final.

**Non-Goals:** relevancia, cercanía, conversión de moneda.

## Decisions

| `sort` | `order` | `ORDER BY` |
|---|---|---|
| `published_at` | `desc` (por defecto) | `published_at DESC, id DESC` |
| `published_at` | `asc` | `published_at ASC, id ASC` |
| `price` | `asc` | `price ASC NULLS LAST, published_at DESC, id DESC` |
| `price` | `desc` | `price DESC NULLS LAST, published_at DESC, id DESC` |

- **`order` por defecto `desc`** también con `sort=price` (contrato); la interfaz envía `asc` para «más baratos primero».
- **Sin conversión de moneda:** en el MVP todos los precios están en EUR.
- **Valores fuera del enum → 422** por la validación de FastAPI.

## Risks / Trade-offs

- [Varias monedas en el futuro] → requeriría normalizar el precio antes de ordenar.
