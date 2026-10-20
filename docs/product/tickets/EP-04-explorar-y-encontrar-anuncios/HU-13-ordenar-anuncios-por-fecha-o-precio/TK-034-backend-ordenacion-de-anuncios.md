# TK-034 · Backend: ordenar anuncios por fecha o precio (`sort`, `order`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (repositorio y endpoint de anuncios) |
| **Historia** | HU-13 Ordenar anuncios por fecha o precio (Épica 4) |
| **Prioridad** | Media |
| **Depende de** | TK-028 |
| **Referencias** | `docs/api/paths/communities_community_id_listings.yaml` (parámetros `sort` y `order`); `readme.md` §3.2 (índice `(price)`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-13 pide ordenar por fecha de publicación o por precio, en ambos sentidos, con los anuncios sin precio siempre al final.

**Objetivo:** añadir los parámetros `sort` (`published_at` | `price`, por defecto `published_at`) y `order` (`asc` | `desc`, por defecto `desc`) al listado.

## 2. Alcance

**Incluye**
- Ordenación por fecha y por precio, con desempate estable.
- Anuncios sin precio al final en ambos sentidos.

**No incluye**
- Ordenar por relevancia (TK-030 §8) o por cercanía.

## 3. Requisitos técnicos

| `sort` | `order` | Cláusula `ORDER BY` |
|---|---|---|
| `published_at` | `desc` (por defecto) | `published_at DESC, id DESC` |
| `published_at` | `asc` | `published_at ASC, id ASC` |
| `price` | `asc` | `price ASC NULLS LAST, published_at DESC, id DESC` |
| `price` | `desc` | `price DESC NULLS LAST, published_at DESC, id DESC` |

- Con `sort=price` y sin `order` explícito, el sentido por defecto sigue siendo `desc` (contrato). El frontend envía `order=asc` para «más baratos primero» (TK-035).
- El precio se compara sin conversión de moneda: todos los anuncios del MVP están en EUR (TK-022 §3.2) (asumido).
- Valores fuera del enum → **422**.
- Combinable con `q`, `type` y `category_id`.

### Pruebas

- Los cuatro órdenes con anuncios con y sin precio y fechas iguales (el desempate no cambia entre páginas).
- `NULLS LAST` en `asc` y en `desc` (HU-13 AC3).
- `sort=title` → `422`.

## 4. Criterios de aceptación

**AC1 — Por fecha (HU-13 AC1)**
- **Given** anuncios con fechas distintas
- **When** llamo con `sort=published_at&order=desc` y después `order=asc`
- **Then** recibo del más reciente al más antiguo, y al revés

**AC2 — Por precio (HU-13 AC2)**
- **Given** anuncios con precios distintos
- **When** llamo con `sort=price&order=asc` y después `order=desc`
- **Then** recibo de menor a mayor precio, y al revés

**AC3 — Sin precio al final (HU-13 AC3)**
- **Given** anuncios sin precio
- **When** ordeno por precio en cualquier sentido
- **Then** los anuncios sin precio aparecen al final

## 5. Plan de tareas

1. `sort` y `order` en `ListingQuery` y en el repositorio.
2. Parámetros del endpoint y pruebas; verificación según la sección 6.

## 6. Verificación

```bash
curl -s "http://localhost:8000/v1/communities/<id>/listings?sort=price&order=asc" -H "Authorization: Bearer $MIEMBRO"
curl -s "http://localhost:8000/v1/communities/<id>/listings?sort=price&order=desc" -H "Authorization: Bearer $MIEMBRO"
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `pytest` y `ruff check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Rendimiento de `ORDER BY price` filtrado por comunidad:** el índice `(price)` del README no incluye `community_id`; si hiciera falta, índice `(community_id, price)`.
