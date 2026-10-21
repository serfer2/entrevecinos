# TK-050 · Backend: comunidades pendientes de aprobación (`POST /v1/communities`, `GET/PATCH /v1/admin/communities`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `communities`, router `admin`), `docs/api/` |
| **Historia** | HU-21 Aprobar las comunidades nuevas antes de activarlas (Épica 8) |
| **Prioridad** | Alta |
| **Depende de** | TK-013, TK-015, TK-017 |
| **Referencias** | `docs/api/paths/communities.yaml` (`post`), `admin_communities.yaml`, `admin_communities_community_id.yaml`; esquemas `Community`, `AdminCommunityUpdate` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Hoy `POST /communities` crea la comunidad activa. HU-21 pide que quede pendiente hasta que un `platform_admin` la apruebe. El contrato ya define, fuera del MVP, `GET /admin/communities` (con filtro `is_active`) y `PATCH /admin/communities/{id}` (activar o desactivar).

**Objetivo:** crear las comunidades con `is_active = false` y pasar al MVP los dos endpoints de administración, limitados a listar y aprobar (activar).

## 2. Alcance

**Incluye**
- `POST /communities`: la comunidad se crea con `is_active = false`; el creador sigue quedando como `community_admin` aprobado.
- `GET /admin/communities` y `PATCH /admin/communities/{id}` (solo `is_active: true`), con `x-mvp: true`.
- Actualizar el contrato y la tabla de cambios de `docs/api/README.md`.

**No incluye**
- Desactivar comunidades (`is_active: false`): en el MVP una comunidad inactiva es una comunidad pendiente (asumido); se rechaza con `422`.
- Rechazar una comunidad pendiente (sin historia; asumido).
- Que el `platform_admin` cree comunidades ya activas (TK-052).

## 3. Requisitos técnicos

### 3.1 Creación pendiente

- `CommunityRepository.add(community, admin_id, is_active)`; `CreateCommunity` pasa `is_active=False`.
- Sin migración: la columna `community.is_active` ya existe. Las comunidades actuales siguen activas.
- Una comunidad inactiva ya se comporta como pendiente: `GET /communities/{id}` y todo lo que pasa por `CommunityAccess` responden `404`, no aparece en `GET /communities`, y `GET /users/me/memberships` se la devuelve a su creador porque su membresía está aprobada.

### 3.2 `GET /v1/admin/communities`

- Solo `platform_admin`; resto → `403`.
- `is_active` (opcional) filtra; sin él, todas. Paginado (`page`, `page_size`).
- Orden: `created_at` y `id` ascendentes (las pendientes más antiguas primero; asumido).
- Nuevo método `CommunityRepository.list_all(is_active, page)` y caso de uso `ListAllCommunities`.

### 3.3 `PATCH /v1/admin/communities/{id}`

- Solo `platform_admin`; resto → `403`. Comunidad inexistente → `404`.
- Cuerpo `{"is_active": true}` (`extra="forbid"`); `is_active: false` → `422`.
- Activa la comunidad (idempotente si ya lo estaba) y devuelve `200` con `Community`.
- Nuevo método `CommunityRepository.activate(community_id) -> Community | None` (busca también las inactivas) y caso de uso `ApproveCommunity`.

### 3.4 Contrato

- `communities.yaml` (`post`): la comunidad se crea con `is_active: false` y queda pendiente de aprobación.
- `admin_communities.yaml` y `admin_communities_community_id.yaml`: `x-mvp: true`; descripción del uso en el MVP (listar pendientes y aprobar).
- `AdminCommunityUpdate.is_active`: en el MVP solo `true`.
- `README.md`: fila TK-050 en «Cambios» y «Administración» como parcialmente MVP en el resumen.

### 3.5 Pruebas

- Creación: `is_active` falso, creador aprobado, la comunidad no aparece en la búsqueda y su detalle da `404`.
- Admin: listar con y sin filtro, orden, paginación, `403` para usuarios normales, aprobar, idempotencia, `404`, `422` con `false` o campos extra.
- El *helper* de pruebas `create_community` aprueba la comunidad para que el resto de pruebas sigan trabajando con comunidades activas.

## 4. Criterios de aceptación

**AC1 — Comunidad pendiente (HU-21 AC1)**
- **Given** un usuario autenticado
- **When** hace `POST /v1/communities`
- **Then** recibe `201` con `is_active: false`, la comunidad no aparece en `GET /v1/communities` y `GET /v1/communities/{id}` responde `404`

**AC2 — Lista de pendientes (HU-21 AC2)**
- **Given** un `platform_admin`
- **When** hace `GET /v1/admin/communities?is_active=false`
- **Then** recibe las comunidades pendientes, de la más antigua a la más reciente

**AC3 — Aprobación (HU-21 AC3)**
- **Given** un `platform_admin` y una comunidad pendiente
- **When** hace `PATCH /v1/admin/communities/{id}` con `{"is_active": true}`
- **Then** recibe `200` con `is_active: true` y la comunidad aparece en la búsqueda

**AC4 — Restricción (HU-21 AC4)**
- **Given** un usuario sin rol `platform_admin`
- **When** llama a cualquiera de los dos endpoints de administración
- **Then** recibe `403`

## 5. Plan de tareas

1. `add(..., is_active)`, `list_all`, `activate` en el puerto, el repositorio y el *fake*.
2. Casos de uso `CreateCommunity` (pendiente), `ListAllCommunities`, `ApproveCommunity`.
3. Router `admin` y esquemas.
4. Contrato y `docs/api/README.md`.
5. Pruebas y *helper* `create_community`.
6. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec api python -m pytest -q
# Usuario normal: POST /v1/communities → is_active false; GET /v1/communities/{id} → 404
# platform_admin: GET /v1/admin/communities?is_active=false → la lista; PATCH {"is_active": true} → 200
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] Las pruebas de la API y el lint pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **`is_active` con doble significado:** si más adelante se añade la desactivación, hará falta distinguir «pendiente» de «desactivada» (por ejemplo, con `approved_at`).
- **Sin rechazo:** una comunidad que el `platform_admin` no quiere aprobar se queda pendiente para siempre.
