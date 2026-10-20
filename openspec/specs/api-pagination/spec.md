# api-pagination Specification

## Purpose
Parámetros (`page`, `page_size`) y respuesta comunes de los listados paginados.
## Requirements
### Requirement: Paginación común
Los listados paginados SHALL aceptar `page` (≥ 1, por defecto 1) y `page_size` (1–100, por defecto 20) y responder `{items, page, page_size, total}`; valores fuera de rango MUST responder `422`.

#### Scenario: Segunda página
- **WHEN** hay 25 elementos y se pide `page=2&page_size=10`
- **THEN** la respuesta tiene 10 elementos, `page = 2`, `page_size = 10` y `total = 25`

#### Scenario: Más allá del final
- **WHEN** se pide una página posterior a la última
- **THEN** `items` está vacío y `total` es el real

