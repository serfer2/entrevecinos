# TK-030 · Backend y base de datos: búsqueda de anuncios por palabras clave (`q`)

| Campo | Valor |
|---|---|
| **Tipo** | Base de datos / backend |
| **Componente** | `apps/api/` (`migrations/`, repositorio de anuncios) |
| **Historia** | HU-11 Buscar anuncios por palabras clave (Épica 4) |
| **Prioridad** | Media |
| **Depende de** | TK-015 (extensión `unaccent`), TK-028 |
| **Referencias** | `docs/api/paths/communities_community_id_listings.yaml` (parámetro `q`); `readme.md` §3.2 (índice GIN sobre `title` y `description`, columna `tsvector` generada) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-11 pide encontrar los anuncios cuyo título o descripción contienen una palabra clave. El README recomienda búsqueda de texto completo de PostgreSQL con una columna `tsvector` generada y un índice GIN.

**Objetivo:** añadir la búsqueda de texto completo en español, sin distinguir tildes ni mayúsculas, y el parámetro `q` del listado de TK-028.

## 2. Alcance

**Incluye**
- Migración `0005`: configuración de búsqueda `es_unaccent`, columna generada `listing.search_vector` e índice GIN.
- Parámetro `q` (2–160 caracteres tras recortar) en `GET /v1/communities/{id}/listings`, como indica el contrato.

**No incluye**
- Ordenar por relevancia: el contrato solo ordena por fecha o precio (ver §8).
- Búsqueda entre comunidades: siempre dentro de una comunidad.

## 3. Requisitos técnicos

### 3.1 Migración `0005`

```sql
CREATE TEXT SEARCH CONFIGURATION es_unaccent (COPY = spanish);
ALTER TEXT SEARCH CONFIGURATION es_unaccent
  ALTER MAPPING FOR hword, hword_part, word WITH unaccent, spanish_stem;

ALTER TABLE listing ADD COLUMN search_vector tsvector GENERATED ALWAYS AS (
  setweight(to_tsvector('es_unaccent', coalesce(title, '')), 'A') ||
  setweight(to_tsvector('es_unaccent', coalesce(description, '')), 'B')
) STORED;

CREATE INDEX ix_listing_search_vector ON listing USING GIN (search_vector);
```

- `downgrade()` elimina el índice, la columna y la configuración.
- La columna se declara en el modelo ORM como `Computed` para que `alembic check` no detecte diferencias.

### 3.2 Construcción de la consulta

- `q` se recorta; vacío o solo espacios equivale a no enviarlo (HU-11 AC3).
- **Longitud mínima:** si tras recortar tiene 1 carácter → **422** `{"detail": "La búsqueda debe tener al menos 2 caracteres."}` (HU-11 AC4). Se valida en el esquema de la petición, no en la consulta.
- Se divide en palabras (letras y dígitos Unicode) y se descartan las de un solo carácter, que como prefijo («a:*») coincidirían con casi todo; el resto de caracteres se descarta, de modo que el texto del usuario nunca llega a `to_tsquery` sin limpiar.
- Cada palabra se convierte en un prefijo y se combinan con `&`: `bici rojo` → `bici:* & rojo:*`, con `to_tsquery('es_unaccent', :tsquery)` (asumido: el prefijo permite encontrar «bicicleta» escribiendo «bici»).
- Si tras limpiar no queda ninguna palabra, el listado devuelve `items: []` (asumido).
- Filtro: `search_vector @@ to_tsquery(...)`, combinado con `AND` con los filtros de TK-028 (y después de TK-032).
- El orden sigue siendo el de TK-028 (`published_at DESC` por defecto).

### 3.3 Pruebas

- «Bicicleta» encuentra un anuncio con «bicicleta» en el título y otro con «Bicicletas» en la descripción.
- «camion» encuentra «camión»; «BICI» encuentra «bicicleta».
- Varias palabras exigen todas (`AND`).
- Caracteres especiales (`'`, `&`, `:`, `!`, `)`) no provocan errores.
- Sin coincidencias → `items: []`, `total: 0`.
- `q` de 161 caracteres → `422`; `q=a` y `q=%20a%20` → `422`; `q=ab` → `200`.
- `q=bici a` busca solo `bici:*`; `q=a b` (sin palabras válidas) → `items: []`.
- `EXPLAIN` de la consulta usa `ix_listing_search_vector` con datos suficientes.

## 4. Criterios de aceptación

**AC1 — Coincidencias (HU-11 AC1)**
- **Given** anuncios con «bicicleta» en el título o la descripción, y otros sin ella
- **When** llamo al listado con `q=bicicleta` (o `q=Bicicléta`)
- **Then** recibo solo los que la contienen, con `total` correcto

**AC2 — Sin resultados (HU-11 AC2)**
- **Given** que ninguna descripción contiene «patinete»
- **When** busco `q=patinete`
- **Then** recibo `200` con `items: []` y `total: 0`

**AC3 — Limpiar la búsqueda (HU-11 AC3)**
- **Given** el listado
- **When** envío `q=` o `q=%20%20`
- **Then** recibo todos los anuncios visibles, como sin `q`

**AC4 — Búsqueda demasiado corta (HU-11 AC4)**
- **Given** el listado
- **When** envío `q=a`
- **Then** recibo `422` con «La búsqueda debe tener al menos 2 caracteres.»

**AC5 — Entrada segura**
- **Given** el listado
- **When** envío `q=bici'); drop table listing;--` o `q=a & !b`
- **Then** recibo `200` sin errores y la base de datos no se ve afectada

## 5. Plan de tareas

1. Migración `0005` y columna `Computed` en el modelo.
2. Constructor de `tsquery` con pruebas unitarias.
3. Filtro en el repositorio, parámetro `q` y pruebas de integración; verificación según la sección 6.

## 6. Verificación

```bash
make dev
curl -s "http://localhost:8000/v1/communities/<id>/listings?q=bici" -H "Authorization: Bearer $MIEMBRO"
curl -s "http://localhost:8000/v1/communities/<id>/listings?q=camion" -H "Authorization: Bearer $MIEMBRO"
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm api alembic check && $COMPOSE run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] `pytest`, `ruff check` y `alembic check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Relevancia:** los resultados se ordenan por fecha, no por relevancia. Se puede añadir `sort=relevance` (con `ts_rank`) como cambio de contrato.
- **Palabras cortas como prefijo:** con el mínimo de 2 caracteres, «ab:*» aún puede devolver muchos resultados; aceptable con el volumen de una comunidad.
