## Context

TK-012 creó `community`; TK-015 la migración `0003`. Modelo de datos: `readme.md` §3.2.

## Goals / Non-Goals

**Goals:** restricciones en la base de datos (precio y moneda coherentes, una sola portada, orden sin empates), índices recomendados y migración reversible.

**Non-Goals:** búsqueda de texto completo (TK-030); dominio y endpoints (TK-021, TK-022).

## Decisions

- **`CHECK ((price IS NULL) = (currency IS NULL))`:** moneda si y solo si hay precio.
- **Portada única** con un índice único parcial `(listing_id) WHERE is_cover`; orden único `(listing_id, position)`.
- **Índices con `published_at DESC`** con nombre explícito (la convención de nombres no admite expresiones).
- **FK** con `ON DELETE RESTRICT` (borrado lógico), salvo `listing_image.listing_id` (`CASCADE`) y el avatar (`SET NULL`).
- **Categorías iniciales en la migración** (datos, no esquema): `downgrade()` las elimina con la tabla.

## Risks / Trade-offs

- [Las categorías iniciales son una propuesta] → revisables por negocio; gestión por `platform_admin` fuera del MVP.
