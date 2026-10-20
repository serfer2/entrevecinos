# TK-032 · Backend: filtros de anuncios por tipo y categoría

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (repositorio y endpoint de anuncios) |
| **Historia** | HU-12 Filtrar anuncios por comunidad y tipo (Épica 4) |
| **Prioridad** | Media |
| **Depende de** | TK-028 (y TK-030 para la combinación con `q`) |
| **Referencias** | `docs/api/paths/communities_community_id_listings.yaml` (parámetros `type` y `category_id`); `readme.md` §3.2 (índices `(community_id, type, published_at DESC)` y `(category_id, published_at DESC)`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-12 pide filtrar por tipo de anuncio y por comunidad, y combinar los filtros con la búsqueda. El filtro por comunidad ya está implícito en la ruta (`/communities/{id}/listings`): cambiar de comunidad es cambiar de ruta. El contrato añade además `category_id`.

**Objetivo:** añadir los parámetros `type` y `category_id` al listado, combinables entre sí y con `q`.

## 2. Alcance

**Incluye**
- `type` (`ListingType`) y `category_id` (UUID) en `ListingQuery` y en el endpoint.

**No incluye**
- Selección de varios tipos a la vez (el contrato admite uno; ver §8).
- Listado de varias comunidades a la vez: siempre se consulta una comunidad.

## 3. Requisitos técnicos

- `type`: valor de `ListingType` → filtro `listing.type = :type`. Valor desconocido → **422**.
- `category_id`: UUID → filtro `listing.category_id = :id`. Una categoría inexistente o inactiva devuelve una lista vacía (no `422`, asumido: los filtros no validan existencia).
- Todos los filtros se combinan con `AND` (con `q` de TK-030 y el filtro base de visibilidad de TK-028).
- `total` refleja los filtros aplicados.

### Pruebas

- `type=sell` devuelve solo `sell`; `type=foo` → `422`.
- `category_id` válido, inexistente y mal formado (`422`).
- `q=bici&type=sell` devuelve solo los que cumplen ambos.
- Los filtros no saltan la regla de acceso: un ajeno sigue recibiendo `403`.

## 4. Criterios de aceptación

**AC1 — Filtro por tipo (HU-12 AC1)**
- **Given** anuncios de varios tipos
- **When** llamo al listado con `type=sell`
- **Then** recibo solo los de tipo `sell`

**AC2 — Cambio de comunidad (HU-12 AC2)**
- **Given** que soy miembro aprobado de dos comunidades
- **When** llamo al listado de cada una
- **Then** cada respuesta contiene solo los anuncios de esa comunidad

**AC3 — Filtros combinados (HU-12 AC3)**
- **Given** anuncios que cumplen solo la palabra clave, solo el tipo o ambos
- **When** llamo con `q=bici&type=sell`
- **Then** recibo solo los que cumplen ambas condiciones

## 5. Plan de tareas

1. Ampliar `ListingQuery` y el repositorio.
2. Parámetros del endpoint y pruebas; verificación según la sección 6.

## 6. Verificación

```bash
curl -s "http://localhost:8000/v1/communities/<id>/listings?type=sell" -H "Authorization: Bearer $MIEMBRO"
curl -s "http://localhost:8000/v1/communities/<id>/listings?q=bici&type=sell" -H "Authorization: Bearer $MIEMBRO"
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `pytest` y `ruff check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Varios tipos a la vez** (p. ej. «Vendo» y «Regalo»): requeriría `type` como lista en el contrato.
