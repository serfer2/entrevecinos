## Why

HU-11: buscar anuncios por palabras clave en el título y la descripción, con un mensaje cuando no hay resultados y un mínimo de 2 caracteres. Ticket: `docs/product/tickets/EP-04-explorar-y-encontrar-anuncios/HU-11-buscar-anuncios-por-palabras-clave/TK-030-backend-busqueda-de-texto-completo.md`.

## What Changes

- Migración `0005`: configuración `es_unaccent` (español sin tildes), columna generada `listing.search_vector` e índice GIN.
- Parámetro `q` en `GET /v1/communities/{id}/listings`: palabras por prefijo combinadas con `AND`; vacío = sin búsqueda; 1 carácter → 422.

## Capabilities

### New Capabilities

### Modified Capabilities
- `listing-browsing`: búsqueda por palabras clave.

## Impact

- `apps/api` (migración, dominio, repositorio, presentación y pruebas).
