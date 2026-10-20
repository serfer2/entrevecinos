# TK-015 · Backend: buscar comunidades, solicitar el acceso y mis membresías

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (áreas `communities` y `users`; paginación común) |
| **Historia** | HU-05 Seleccionar una comunidad y solicitar el acceso (Épica 2) |
| **Prioridad** | Alta |
| **Depende de** | TK-013 |
| **Referencias** | `docs/api/paths/communities.yaml` (`get`), `communities_community_id_memberships.yaml` (`post`), `users_me_memberships.yaml`; esquemas `Community`, `Membership`, `MyMembership`, `PageMeta`; parámetros `Page`, `PageSize` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-05 pide buscar comunidades por nombre, ciudad o código postal, solicitar el acceso (queda pendiente de aprobación) y no duplicar solicitudes. El usuario también necesita conocer el estado de sus solicitudes.

**Objetivo:** implementar `GET /v1/communities` (búsqueda paginada), `POST /v1/communities/{id}/memberships` y `GET /v1/users/me/memberships`, y crear la paginación común que usarán todos los listados.

## 2. Alcance

**Incluye**
- Paginación común (`page`, `page_size`, respuesta `{items, page, page_size, total}`).
- Búsqueda de comunidades activas.
- Solicitud de acceso (`pending`, `member`) y respuesta `409` con el estado actual.
- Listado de mis membresías con la comunidad embebida.

**No incluye**
- Aprobación o rechazo (TK-017). Bloqueo y expulsión (TK-040).
- Bloqueo del acceso a los anuncios para membresías no aprobadas: se aplica en los endpoints de anuncios (TK-022, TK-028) mediante la política de TK-017.

## 3. Requisitos técnicos

### 3.1 Paginación común

- `presentation/v1/pagination.py`: dependencia `PageParams` (`page ≥ 1`, por defecto 1; `1 ≤ page_size ≤ 100`, por defecto 20) y modelo genérico `Page[T]` (`items`, `page`, `page_size`, `total`).
- `application/pagination.py`: `PageRequest(page, page_size)` y `PageResult[T](items, total)`, sin dependencias de framework.
- Pedir una página más allá del final devuelve `items: []` con el `total` real (asumido).

### 3.2 `GET /v1/communities` (autenticado)

- Parámetros: `q` (≤160, busca en `name` y `description`), `city` (≤120), `postal_code` (≤16), `page`, `page_size`.
- Coincidencias sin distinguir mayúsculas ni tildes (asumido): `unaccent(lower(col)) LIKE unaccent(lower('%' || :term || '%'))`. La migración `0003` activa la extensión `unaccent` y crea una función inmutable `f_unaccent(text)` para poder indexarla más adelante.
- Los parámetros se combinan con `AND`. `postal_code` busca por prefijo (`28220` encuentra `28220`; `282` encuentra `282xx`) (asumido).
- Los comodines `%` y `_` del usuario se escapan.
- Orden: `name` ascendente y después `created_at` (estable).
- Solo comunidades `is_active = true`.

### 3.3 `POST /v1/communities/{community_id}/memberships` (autenticado, sin cuerpo)

- Crea la membresía del usuario autenticado con `role = member`, `status = pending`.
- **201**: `Membership` (`community_id`, `user` = `UserSummary`, `role`, `status`, `requested_at`…).
- **404**: comunidad inexistente o desactivada.
- **409**: ya existe una membresía en cualquier estado. Cuerpo: `{"detail": "Ya tienes una membresía en esta comunidad.", "status": "<estado actual>"}` (asumido: el campo `status` extra permite al frontend mostrar el estado, HU-05 AC4; TK-017 §3.4 lo documenta en el contrato como `MembershipConflict`).
- La concurrencia la cubre la PK compuesta: la violación se traduce también a `409`.

### 3.4 `GET /v1/users/me/memberships` (autenticado)

- Parámetro opcional `status`.
- **200**: `{items: MyMembership[]}` (sin paginar, como en el contrato: un usuario pertenece a pocas comunidades), ordenado por `requested_at` descendente.
- Incluye comunidades desactivadas solo si la membresía está `approved` (asumido).

### 3.5 Diseño por capas

- `CommunityRepository.search(filters, page) -> PageResult[Community]`.
- `MembershipRepository`: `get(community_id, user_id)`, `add_request(community_id, user_id) -> Membership`, `list_for_user(user_id, status) -> list[MyMembership]`.
- Casos de uso: `SearchCommunities`, `RequestMembership` (lanza `MembershipAlreadyExists(status)`), `ListMyMemberships`.

## 4. Criterios de aceptación

**AC1 — Búsqueda (HU-05 AC1)**
- **Given** las comunidades «Urbanización Los Olivos» (Majadahonda, 28220) y «Barrio del Pilar» (Madrid, 28029)
- **When** busco `q=olivos`, `city=majadahonda`, `postal_code=28220` o `q=Olívos`
- **Then** en todos los casos recibo solo «Urbanización Los Olivos», con `total = 1`

**AC2 — Paginación**
- **Given** 25 comunidades que coinciden
- **When** pido `page=2&page_size=10`
- **Then** recibo 10 elementos, `page = 2`, `page_size = 10` y `total = 25`; `page_size=101` → `422`

**AC3 — Solicitud de acceso (HU-05 AC2)**
- **Given** una comunidad de la que no soy miembro
- **When** envío `POST /v1/communities/{id}/memberships`
- **Then** recibo `201` con `status: "pending"` y `role: "member"`, y aparece en `GET /v1/users/me/memberships`

**AC4 — Solicitud duplicada (HU-05 AC4)**
- **Given** que ya tengo una membresía pendiente, aprobada, rechazada o bloqueada en la comunidad
- **When** vuelvo a solicitar el acceso
- **Then** recibo `409` con mi estado actual y no se crea una segunda membresía

## 5. Plan de tareas

1. Paginación común (aplicación y presentación).
2. Migración `0003` (`unaccent` y `f_unaccent`).
3. Búsqueda de comunidades (repositorio, caso de uso, endpoint) y pruebas.
4. Solicitud de acceso con `409` y pruebas (incluida la carrera por la PK).
5. `GET /users/me/memberships` y pruebas.
6. Verificar según la sección 6 (el contrato del `409` con `status` lo documenta TK-017 §3.4).

## 6. Verificación

```bash
make dev
curl -s "http://localhost:8000/v1/communities?q=olivos" -H "Authorization: Bearer $TOKEN"
curl -s -X POST http://localhost:8000/v1/communities/<id>/memberships -H "Authorization: Bearer $TOKEN"  # 201
curl -s -X POST http://localhost:8000/v1/communities/<id>/memberships -H "Authorization: Bearer $TOKEN"  # 409
curl -s http://localhost:8000/v1/users/me/memberships -H "Authorization: Bearer $TOKEN"
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] La paginación común está documentada en `apps/api/README.md`.
- [ ] `pytest`, `ruff check` y `alembic check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Rendimiento de `LIKE '%…%'`:** sin índice; suficiente para el volumen del MVP. Si crece, índice GIN de trigramas (`pg_trgm`) sobre `f_unaccent(lower(name))`.
- **Volver a solicitar tras un rechazo:** el contrato responde `409` en cualquier estado, así que un rechazo es definitivo hasta que un administrador elimine la membresía (TK-040). Revisar con negocio.
