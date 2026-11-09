# TK-109 · Backend: cambiar el rol de un miembro (solo `platform_admin`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad (con contrato) |
| **Componente** | `apps/api/` (área `communities`), `docs/api/` |
| **Historia** | HU-45 Nombrar a los administradores de una comunidad (Épica 8) |
| **Prioridad** | Alta |
| **Depende de** | TK-017, TK-040, TK-070 |
| **Referencias** | `application/communities/review_membership.py` (`ChangeMembershipStatus`, `RemoveMembership`); `presentation/v1/communities.py` (`update_membership`); `presentation/v1/schemas/communities.py` (`MembershipUpdateRequest`); `docs/api/paths/communities_community_id_memberships_user_id.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Hoy solo es `community_admin` quien crea la comunidad (`CreateCommunity`). El contrato ya prevé `role` en `MembershipUpdate`, pero la API lo rechaza con `422` («**Pendiente:** `role` se rechaza con 422») porque no tenía historia. HU-45 encarga al `platform_admin` decidir quién administra cada comunidad.

**Objetivo:** permitir que un `platform_admin` cambie el rol de un miembro aprobado entre `member` y `community_admin` con `PATCH /v1/communities/{community_id}/memberships/{user_id}` y `{"role": …}`, sin dejar nunca una comunidad sin administrador.

## 2. Alcance

**Incluye**
- `role` en `MembershipUpdateRequest`, con valores `member` o `community_admin`.
- Caso de uso `ChangeMembershipRole` y método `set_role` del repositorio.
- Reglas: solo `platform_admin`, solo membresías aprobadas y al menos un administrador.
- Contrato y tabla de cambios de `docs/api/README.md`.

**No incluye**
- El rol `moderator` (sin historia: `422`).
- Que un `community_admin` nombre a otros administradores (HU-45 AC6; ver §8).
- Avisos por correo del cambio de rol (asumido; ver §8).
- Cambios de esquema de BD: `community_memberships.role` ya existe.

## 3. Requisitos técnicos

### 3.1 Petición

- `MembershipUpdateRequest` admite **exactamente uno** de `status` o `role` (validador de Pydantic; ambos o ninguno → `422`). Mezclar revisión y cambio de rol en una petición complica los errores y no lo necesita la web (asumido).
- `role: Literal[MembershipRole.MEMBER, MembershipRole.COMMUNITY_ADMIN]`; `moderator` → `422`.
- Se mantiene `extra="forbid"`.

### 3.2 Caso de uso `ChangeMembershipRole`

En `application/communities/` (junto a `ChangeMembershipStatus`):

1. El actor debe ser `platform_admin`; si no → `PermissionDenied` (`403`). No se usa `require_role` con `COMMUNITY_ADMINS`, porque los administradores de la comunidad **no** pueden cambiar roles. La comprobación de que la comunidad existe se hace con `CommunityAccess.membership` / `require_role` (`404` si no existe), igual que en el resto de endpoints.
2. La membresía del usuario debe existir → si no, `MembershipNotFound` (`404`).
3. La membresía debe estar `approved`; si no → `MembershipChangeRejected(ONLY_APPROVED)` (`409`) con el detalle «Solo se puede cambiar el rol de un miembro aprobado.».
4. Mismo rol que el actual → se devuelve la membresía sin cambios (`200`, idempotente).
5. De `community_admin` a `member` con `count_admins(community_id) <= 1` → `MembershipChangeRejected(LAST_ADMIN)` (`409`), con el mensaje existente «La comunidad debe tener al menos un administrador.».
6. `memberships.set_role(community_id, user_id, role)` → `MembershipDetail`.

`ChangeMembershipStatus` no cambia: sigue sin dejar bloquear a un administrador. Para bloquearlo, primero se le quita el rol.

### 3.3 Repositorio

- Puerto `MembershipRepository.set_role(community_id, user_id, role) -> MembershipDetail`.
- SQLAlchemy: fija `role` y devuelve el detalle con `detail_to_domain`. No toca `reviewed_by`/`reviewed_at`, que describen la revisión de la solicitud (asumido).
- Para el último administrador (§3.2.5), el recuento y la actualización se hacen en la misma transacción bloqueando las membresías de administrador de la comunidad (`SELECT … FOR UPDATE`). Así, dos degradaciones simultáneas no dejan la comunidad sin administrador.

### 3.4 Endpoint

- `update_membership` despacha según el campo: `status` → `ChangeMembershipStatus` (con el aviso de TK-108); `role` → `ChangeMembershipRole` (sin correo).
- La respuesta sigue siendo `MembershipResponse`.
- Errores: `403`, `404`, `409` y `422`, como en §3.1–3.2.

### 3.5 Contrato y documentación

- `docs/api/paths/communities_community_id_memberships_user_id.yaml`: la descripción del `PATCH` sustituye «solo un `community_admin` puede asignar el rol `community_admin`» por «solo `platform_admin` cambia `role` (`member` ↔ `community_admin`) de una membresía aprobada; se envía `status` o `role`, no ambos; sin dejar la comunidad sin administrador (`409`)». Añade la respuesta `409` (`Conflict`) si falta, y un segundo ejemplo con `role: community_admin`.
- `MembershipUpdate.yaml`: `oneOf`/descripción que refleje «exactamente uno» y que `moderator` no está disponible en el MVP.
- `docs/api/README.md`: fila TK-109 en «Cambios».
- Se elimina la nota «**Pendiente:** `role` se rechaza con 422» de la descripción del endpoint en FastAPI.
- `npx @redocly/cli lint` sin errores.

### 3.6 Pruebas

- **Unitarias** (`ChangeMembershipRole`, con *fakes*): nombrar administrador; quitar el rol con otro administrador; último administrador → `409`; membresía `pending`, `rejected` o `blocked` → `409`; mismo rol → sin cambios; `community_admin` y `member` como actores → `PermissionDenied`; comunidad o membresía inexistentes → `404`.
- **Endpoint** (`@pytest.mark.db`): `platform_admin` nombra y degrada (`200`, `role` en la respuesta); `community_admin` → `403`; `status` + `role` → `422`; `moderator` → `422`; último administrador → `409`. El nuevo administrador puede llamar a `listCommunityMemberships` (`200`) y el degradado recibe `403`.
- **Integración con TK-106:** tras nombrarlo, el nuevo administrador figura en `list_admin_recipients`.

## 4. Criterios de aceptación

**AC1 — Nombrar administrador (HU-45 AC2)**
- **Given** un miembro aprobado con rol `member`
- **When** un `platform_admin` envía `PATCH … {"role": "community_admin"}`
- **Then** recibe `200` con `role: community_admin`, y ese usuario puede gestionar solicitudes y miembros

**AC2 — Quitar el rol (HU-45 AC3)**
- **Given** una comunidad con dos administradores
- **When** un `platform_admin` envía `{"role": "member"}` para uno de ellos
- **Then** recibe `200`; el usuario sigue `approved` y recibe `403` en la gestión

**AC3 — Último administrador (HU-45 AC4)**
- **Given** una comunidad con un solo administrador
- **When** se le intenta quitar el rol
- **Then** se recibe `409` con «La comunidad debe tener al menos un administrador.»

**AC4 — Solo miembros aprobados (HU-45 AC5)**
- **Given** una membresía `pending`, `rejected` o `blocked`
- **When** se envía `role`
- **Then** se recibe `409` y el rol no cambia

**AC5 — Solo `platform_admin` (HU-45 AC6)**
- **Given** un `community_admin` o un miembro
- **When** envía `role`
- **Then** recibe `403`

## 5. Plan de tareas

1. Validación de `MembershipUpdateRequest` (exactamente uno, `role` permitido).
2. Puerto y repositorio `set_role` con bloqueo.
3. `ChangeMembershipRole` y errores nuevos.
4. Despacho en `update_membership`.
5. Contrato y `docs/api/README.md`.
6. Pruebas y verificación (§6).

## 6. Verificación

```bash
make build-backend && make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
$COMPOSE run --rm api ruff check . && $COMPOSE run --rm api ruff format --check .
# http://localhost:8000/docs → PATCH updateMembership con {"role": "community_admin"} como platform_admin
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Pruebas de la API, `ruff` y `redocly lint` pasan.
- [x] Contrato y `docs/api/README.md` actualizados.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Quién nombra:** el contrato decía que un `community_admin` asigna el rol; HU-45 lo reserva al `platform_admin` para que la plataforma controle quién gestiona cada comunidad. Delegarlo en los administradores de la comunidad sería otra historia y solo cambiaría la comprobación de §3.2.1.
- **Sin aviso por correo:** el nombramiento no avisa al interesado (sin coste de cupo). Si se quisiera, reutilizaría `MembershipNotices` como TK-108.
- **`platform_admin` sin membresía:** no puede nombrarse administrador de una comunidad en la que no es miembro, y no lo necesita: ya la gestiona (HU-31).
