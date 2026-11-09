# TK-112 · Backend: rechazar una comunidad pendiente

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad (con contrato) |
| **Componente** | `apps/api/` (área `communities`), `docs/api/` |
| **Historia** | HU-47 Rechazar una comunidad pendiente (Épica 8) |
| **Prioridad** | Media |
| **Depende de** | TK-050, TK-053 |
| **Referencias** | `application/communities/approve_communities.py` (`ApproveCommunity`, `_require_platform_admin`); `infrastructure/communities/sqlalchemy_community_repository.py` (`activate`, `has_pending`); `presentation/v1/admin.py`; `docs/api/paths/admin_communities_community_id.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El `platform_admin` puede aprobar una comunidad pendiente (`PATCH /v1/admin/communities/{id}` con `is_active: true`), pero no rechazarla. Una comunidad que no procede se queda pendiente para siempre, y su creador no puede crear otra porque solo se admite una pendiente por usuario (TK-053).

**Objetivo:** `DELETE /v1/admin/communities/{community_id}` elimina una comunidad pendiente. Solo `platform_admin`.

## 2. Alcance

**Incluye**
- Operación `adminRejectCommunity` (`DELETE`, `x-mvp: true`).
- Caso de uso `RejectCommunity` y método `delete_pending` del repositorio.
- Contrato y tabla de cambios.

**No incluye**
- Desactivar o borrar comunidades activas (HU-47 AC3).
- Avisar por correo al creador (ver §8).
- La web (TK-113).

## 3. Requisitos técnicos

### 3.1 Semántica: rechazar es eliminar

- Se elimina la fila de `community`. Su única membresía, la del creador como administrador, se borra en cascada (`community_membership.community_id ON DELETE CASCADE`). No hace falta migración.
- Una comunidad pendiente no puede tener anuncios ni otras membresías: `CommunityAccess` responde `404` para las inactivas. Aun así, `listing.community_id` es `ON DELETE RESTRICT`; si alguna vez hubiera anuncios, el borrado fallaría en vez de perder datos (ver §8).
- Al desaparecer la pendiente, `has_pending(creator)` vuelve a ser falso y el creador puede crear otra comunidad (HU-47 AC2).

### 3.2 Caso de uso `RejectCommunity`

En `approve_communities.py`, junto a `ApproveCommunity`:

1. `_require_platform_admin(user)`; si no, `PermissionDenied` (`403`).
2. `communities.delete_pending(community_id)`, que devuelve el resultado: `deleted`, `active` o `missing`.
3. `missing` → `CommunityNotFound` (`404`); `active` → nuevo `CommunityNotPending` (`409`, «Solo se pueden rechazar comunidades pendientes de aprobación.»).

### 3.3 Repositorio

- `CommunityRepository.delete_pending(community_id)`: lee la comunidad con `FOR UPDATE` y solo la borra si `is_active = false`. Así no se puede borrar una comunidad que otro administrador acaba de aprobar.
- `get` sigue devolviendo `None` para las inactivas; `delete_pending` no lo usa.

### 3.4 Endpoint y errores

- `presentation/v1/admin.py`: `@router.delete("/communities/{community_id}", status_code=204, operation_id="adminRejectCommunity")`, con las respuestas `401`, `403`, `404`, `409` y `422` (identificador no válido).
- Manejador de `CommunityNotPending` → `409 {"detail": "Solo se pueden rechazar comunidades pendientes de aprobación."}`, junto a los demás de `presentation/errors.py`.

### 3.5 Contrato

- `docs/api/paths/admin_communities_community_id.yaml`: nueva operación `delete` (`adminRejectCommunity`, tag Administración, `x-mvp: true`). La descripción explica que solo es para `platform_admin`, que solo admite comunidades pendientes, que elimina la comunidad y la membresía de su creador, y que el creador puede crear otra.
- Fila TK-112 en «Cambios» de `docs/api/README.md`, y `DELETE /admin/communities/{community_id}` en la fila «Administración» del resumen de endpoints.
- `npx @redocly/cli lint` sin errores. Si `test_contract_scope.py` compara las operaciones `x-mvp` con las rutas, la prueba debe seguir pasando.

### 3.6 Documentación

- `readme.md` §1.2 «Comunidades y zonas» y MVP «Comunidades»: el administrador de la plataforma aprueba o rechaza las comunidades pendientes. Un rechazo elimina la comunidad y su creador puede crear otra.
- `readme.md` §3.2: añadir `DELETE /admin/communities/{community_id}` a las operaciones de `community`.
- `apps/api/README.md`, «Comunidades»: `RejectCommunity`, `delete_pending` con bloqueo y respuestas (`204`, `404`, `409`).

### 3.7 Pruebas

- **Unitarias** (`RejectCommunity` con *fakes*): rechazo de una pendiente; activa → `CommunityNotPending`; inexistente → `CommunityNotFound`; usuario sin rol de plataforma → `PermissionDenied`.
- **Endpoint** (`@pytest.mark.db`):
  - `204`, y después la comunidad no está en `adminListCommunities` ni en `GET /v1/users/me/memberships` del creador;
  - el creador puede crear otra (`201`);
  - con una comunidad activa → `409`;
  - con un identificador inexistente → `404`;
  - un vecino o un `community_admin` → `403`.

## 4. Criterios de aceptación

**AC1 — Rechazar (HU-47 AC1 y AC2)**
- **Given** una comunidad pendiente creada por un vecino
- **When** un `platform_admin` envía `DELETE /v1/admin/communities/{id}`
- **Then** recibe `204`, la comunidad deja de aparecer en el listado de administración y en las comunidades del creador, y el creador puede crear otra

**AC2 — Solo pendientes (HU-47 AC3)**
- **Given** una comunidad activa
- **When** se envía el `DELETE`
- **Then** se recibe `409` y la comunidad sigue activa

**AC3 — Restricción (HU-47 AC4)**
- **Given** un usuario que no es `platform_admin`
- **When** envía el `DELETE`
- **Then** recibe `403`

## 5. Plan de tareas

1. `CommunityNotPending` y su manejador.
2. `delete_pending` (puerto, SQLAlchemy y *fake*).
3. `RejectCommunity` y endpoint.
4. Contrato y documentación (§3.5 y §3.6).
5. Pruebas y verificación (§6).

## 6. Verificación

```bash
make build-backend && make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
$COMPOSE run --rm api ruff check . && $COMPOSE run --rm api ruff format --check .
# http://localhost:8000/docs → DELETE adminRejectCommunity como platform_admin
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Pruebas de la API, `ruff` y `redocly lint` pasan.
- [x] Documentación actualizada: contrato, `docs/api/README.md`, `readme.md` (§1.2, MVP y §3.2) y `apps/api/README.md` (§3.5 y §3.6).
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Borrar o marcar como rechazada:** borrar es lo más simple (sin migración ni estado nuevo) y libera al creador. Se pierde el historial de rechazos y no se puede impedir que el mismo vecino vuelva a crear la misma comunidad. Si eso llegara a ser un problema, se añadiría un estado `rejected` con su migración.
- **Sin aviso al creador:** su comunidad desaparece de «Mis comunidades» sin explicación. Un correo con el motivo, análogo a HU-44, sería otra historia; se recomienda planificarla junto a HU-47.
- **Anuncios en una pendiente:** no deberían existir; si existieran, el `RESTRICT` hace fallar el borrado con `500` en lugar de perder datos. Se acepta por ser un caso imposible con las reglas actuales.
