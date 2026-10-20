# TK-028 · Backend: listado de anuncios de una comunidad (`GET /v1/communities/{id}/listings`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `listings`) |
| **Historia** | HU-10 Ver los anuncios de mi comunidad (Épica 4) |
| **Prioridad** | Alta (base de HU-11, HU-12 y HU-13) |
| **Depende de** | TK-017, TK-022, TK-026 |
| **Referencias** | `docs/api/paths/communities_community_id_listings.yaml` (`get`); esquemas `Listing`, `PageMeta`; `readme.md` §3.2 (índice `(community_id, status, published_at DESC)`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-10 pide que un miembro aprobado vea los anuncios de su comunidad, primero los más recientes, y que nadie más pueda verlos. Es la base sobre la que HU-11, HU-12 y HU-13 añaden búsqueda, filtros y ordenación.

**Objetivo:** implementar el listado paginado de anuncios visibles de una comunidad, con la estructura de consulta preparada para añadir `q`, `type`, `category_id`, `sort` y `order`.

## 2. Alcance

**Incluye**
- `GET /v1/communities/{id}/listings` con `page` y `page_size`, orden por defecto `published_at DESC`.
- Objeto de consulta `ListingQuery` (aplicación) extensible.
- Solo anuncios `active` y `reserved`, no eliminados.

**No incluye**
- `q` (TK-030), `type` y `category_id` (TK-032), `sort` y `order` (TK-034). Hasta entonces, esos parámetros responden `422` si se envían (asumido: mejor que ignorarlos en silencio).

## 3. Requisitos técnicos

### 3.1 Acceso

- `CommunityAccess.require_member`: **403** para membresías no aprobadas (con `status`, para el aviso de pendiente de HU-05 AC3) y para ajenos; **404** si la comunidad no existe.

### 3.2 Consulta

- `ListingQuery(community_id, page: PageRequest, text=None, type=None, category_id=None, sort="published_at", order="desc")`.
- `WHERE community_id = :id AND status IN ('active', 'reserved') AND deleted_at IS NULL`.
- TK-040 añade a este filtro común que el autor tenga membresía `approved` (oculta los anuncios de miembros bloqueados); conviene centralizar el filtro en un único método del repositorio para que listado, búsqueda y `total` lo compartan.
- Orden por defecto `published_at DESC, id DESC` (desempate estable para que la paginación no repita ni pierda elementos).
- `total` con un `COUNT(*)` sobre el mismo filtro.
- Carga de propietario e imágenes sin N+1 (reutiliza la lectura de TK-022 §3.4). Para el listado basta con la portada, pero se devuelve `Listing` completo por coherencia con el contrato (asumido; si pesa, se puede añadir un esquema resumido).

### 3.3 Respuesta

- **200** `Page[Listing]`. Comunidad sin anuncios → `items: []`, `total: 0`.

### 3.4 Pruebas

- Orden por fecha descendente y desempate estable; paginación (`total`, última página).
- Excluye `hidden`, `completed`, `draft` y eliminados; incluye `reserved`.
- Solo anuncios de esa comunidad.
- Pendiente (**403** con `status`), ajeno (**403**), sin token (**401**), comunidad inexistente (**404**).
- Consulta con 10 anuncios y 3 imágenes cada uno en un número fijo de sentencias SQL (evita N+1; contar con un *listener* de SQLAlchemy).

## 4. Criterios de aceptación

**AC1 — Listado (HU-10 AC1)**
- **Given** que soy miembro aprobado de una comunidad con anuncios
- **When** llamo a `GET /v1/communities/{id}/listings`
- **Then** recibo sus anuncios visibles con título, tipo, precio, imágenes (portada marcada) y `published_at`

**AC2 — Orden por defecto (HU-10 AC2)**
- **Given** anuncios publicados en fechas distintas
- **When** llamo sin parámetros de orden
- **Then** aparecen del más reciente al más antiguo

**AC3 — Comunidad sin anuncios (HU-10 AC3)**
- **Given** una comunidad sin anuncios visibles
- **When** llamo al listado
- **Then** recibo `200` con `items: []` y `total: 0`

**AC4 — Acceso restringido (HU-10 AC4)**
- **Given** que no soy miembro aprobado
- **When** llamo al listado
- **Then** recibo `403` y ningún anuncio

## 5. Plan de tareas

1. `ListingQuery` y repositorio (`search(query) -> PageResult[Listing]`).
2. Caso de uso `ListCommunityListings` con pruebas unitarias.
3. Endpoint, pruebas de integración y de número de consultas; verificación según la sección 6.

## 6. Verificación

```bash
make dev
curl -s "http://localhost:8000/v1/communities/<id>/listings?page=1&page_size=5" -H "Authorization: Bearer $MIEMBRO"
curl -s -o /dev/null -w '%{http_code}\n' "http://localhost:8000/v1/communities/<id>/listings" -H "Authorization: Bearer $PENDIENTE"  # 403
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] La consulta usa el índice `(community_id, status, published_at DESC)` (`EXPLAIN` en la revisión).
- [ ] `pytest` y `ruff check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Tamaño de la respuesta:** `Listing` completo por elemento; aceptable con `page_size ≤ 100`.
