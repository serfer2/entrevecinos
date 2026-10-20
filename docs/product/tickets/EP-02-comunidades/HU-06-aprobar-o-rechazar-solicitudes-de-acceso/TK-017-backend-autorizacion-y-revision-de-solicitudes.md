# TK-017 · Backend: autorización por comunidad y revisión de solicitudes

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad y seguridad (RBAC) |
| **Componente** | `apps/api/` (áreas `communities`, `application/authorization/`) |
| **Historia** | HU-06 Aprobar o rechazar solicitudes de acceso (Épica 2) |
| **Prioridad** | Alta (bloquea todos los endpoints que dependen del rol en una comunidad) |
| **Depende de** | TK-015 |
| **Referencias** | `docs/api/paths/communities_community_id_memberships.yaml` (`get`), `communities_community_id_memberships_user_id.yaml` (`patch`); esquemas `Membership`, `MembershipUpdate`; `components/responses/Forbidden.yaml`; `readme.md` §2.5 (RBAC) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-06 pide que el administrador de una comunidad vea las solicitudes pendientes y las apruebe o rechace, y que un miembro sin ese rol no pueda hacerlo. El README exige que los permisos se comprueben siempre en la API (RBAC).

**Objetivo:** crear la política de autorización por comunidad, que reutilizarán anuncios y administración, e implementar el listado de membresías y la revisión de solicitudes.

## 2. Alcance

**Incluye**
- Política `CommunityAccess` en la capa de aplicación y error de dominio `PermissionDenied` → `403`.
- `GET /v1/communities/{id}/memberships` (filtro `status`, paginado).
- `PATCH /v1/communities/{id}/memberships/{user_id}` con `status` `approved` o `rejected`.
- Extensión del contrato en `docs/api`: campo `status` en el `403` de membresía no aprobada (y en el `409` de TK-015).

**No incluye**
- Bloqueo (`status: blocked`), expulsión (`DELETE`) y cambio de rol (`role`): TK-040.
- Rol `moderator`: se trata igual que `member` salvo en la retirada de anuncios (TK-042); su asignación queda fuera del MVP.
- `platform_admin`: tiene los mismos permisos que un `community_admin` en todas las comunidades, como indica el contrato.

## 3. Requisitos técnicos

### 3.1 Política `CommunityAccess`

`application/authorization/community_access.py` (sin dependencias de framework):

```python
class CommunityAccess:
    def __init__(self, memberships: MembershipRepository) -> None: ...
    def require_member(self, user: User, community_id: UUID) -> Membership: ...
    def require_role(self, user: User, community_id: UUID, roles: set[MembershipRole]) -> Membership | None: ...
```

- `require_member`: exige membresía `approved`. Lanza `MembershipNotApproved(status)` si existe pero no está aprobada (para mostrar «pendiente», HU-05 AC3) o `PermissionDenied` si no existe. Los `platform_admin` pasan siempre.
- `require_role`: exige membresía `approved` con uno de los roles indicados (o `platform_admin`).
- Antes de comprobar permisos se comprueba que la comunidad existe (`404` si no). Aceptado en el contrato: la existencia de comunidades no es secreta (TK-013 §3.3).

Traducción en presentación:

| Error | HTTP | Cuerpo |
|---|---|---|
| `PermissionDenied` | `403` | `{"detail": "No tienes permisos para realizar esta acción."}` |
| `MembershipNotApproved(status)` | `403` | `{"detail": "Tu membresía en esta comunidad no está aprobada.", "status": "<estado>"}` |

### 3.2 `GET /v1/communities/{id}/memberships`

- Requiere `community_admin` (o `moderator`, según el contrato) de la comunidad, o `platform_admin`.
- Parámetros: `status` opcional, `page`, `page_size` (paginación de TK-015).
- Orden: `requested_at` ascendente (las solicitudes más antiguas primero) (asumido).
- **200**: `Page[Membership]`, con `user` como `UserSummary` (`id`, `full_name`, `avatar_url`). No se exponen el correo ni el teléfono del solicitante (asumido).

### 3.3 `PATCH /v1/communities/{id}/memberships/{user_id}`

- Requiere `community_admin` de la comunidad o `platform_admin`.
- **Petición** (`extra="forbid"`): en este ticket solo se admite `{"status": "approved" | "rejected"}`; `blocked` y `role` responden `422` hasta TK-040.
- Transiciones permitidas: `pending → approved` y `pending → rejected`. Cualquier otra (por ejemplo, aprobar una ya rechazada) → `409 {"detail": "La solicitud ya se ha revisado."}` (asumido).
- Al aprobar: `reviewed_by`, `reviewed_at` y `joined_at`. Al rechazar: `reviewed_by` y `reviewed_at`.
- **200**: `Membership` actualizada. **404**: no existe esa membresía.

### 3.4 Contrato: campo `status` en el `403`

El esquema `Error` solo tiene `detail`, así que el `status` de §3.1 (y el del `409` de TK-015) es una extensión del contrato que se documenta en `docs/api`:

- `components/schemas/MembershipError.yaml`: `allOf` de `Error` más `status` (`$ref: MembershipStatus.yaml`, obligatorio).
- `components/responses/MembershipForbidden.yaml` (`403`): `oneOf` de `Error` (sin membresía o sin permisos) y `MembershipError` (membresía no aprobada), con ejemplos de ambos.
- `components/responses/MembershipConflict.yaml` (`409`): `MembershipError`, para `POST /communities/{id}/memberships` (TK-015).
- Sustituir `Forbidden` por `MembershipForbidden` en las operaciones que exigen membresía aprobada: listado y publicación de anuncios, detalle de anuncio, lectura de imágenes y datos de la comunidad que lo requieran (revisar cada `paths/*.yaml` que use `require_member`).
- Registrar los componentes en `openapi.yaml`, pasar `npx @redocly/cli lint openapi.yaml` y regenerar `dist/openapi.bundled.yaml` (`docs/api/README.md`).

### 3.5 Pruebas

- Unitarias de `CommunityAccess`: miembro aprobado, pendiente, rechazado, sin membresía, admin, `platform_admin`.
- Integración: un admin lista y revisa; un miembro aprobado sin rol recibe `403` en ambos endpoints; un usuario ajeno también; transiciones inválidas → `409`; tras aprobar, `GET /users/me/memberships` del solicitante muestra `approved`.

## 4. Criterios de aceptación

**AC1 — Ver solicitudes (HU-06 AC1)**
- **Given** que soy `community_admin` de una comunidad con solicitudes pendientes
- **When** llamo a `GET /v1/communities/{id}/memberships?status=pending`
- **Then** recibo las solicitudes con el nombre de cada solicitante, sin su correo ni su teléfono

**AC2 — Aprobar (HU-06 AC2)**
- **Given** una solicitud pendiente
- **When** envío `PATCH …/memberships/{user_id}` con `{"status": "approved"}`
- **Then** recibo `200` con `status: "approved"`, `reviewed_by` = mi id y `joined_at` informado; el solicitante pasa la comprobación `require_member`

**AC3 — Rechazar (HU-06 AC3)**
- **Given** una solicitud pendiente
- **When** la rechazo
- **Then** queda `rejected`, deja de aparecer con `status=pending` y el solicitante sigue sin acceso

**AC4 — Permiso restringido (HU-06 AC4)**
- **Given** que soy miembro aprobado sin rol de administrador, o no pertenezco a la comunidad
- **When** llamo a cualquiera de los dos endpoints
- **Then** recibo `403 {"detail": "No tienes permisos para realizar esta acción."}` y no se modifica nada

## 5. Plan de tareas

1. `PermissionDenied`, `MembershipNotApproved` y sus manejadores.
2. `CommunityAccess` con pruebas unitarias.
3. Listado de membresías (repositorio, caso de uso, endpoint).
4. Revisión de solicitudes con transiciones y pruebas.
5. Extensión del contrato (§3.4): esquema, respuestas, lint y *bundle*.
6. Documentar en `apps/api/README.md` cómo exigir membresía o rol, y verificar según la sección 6.

## 6. Verificación

```bash
make dev
curl -s "http://localhost:8000/v1/communities/<id>/memberships?status=pending" -H "Authorization: Bearer $ADMIN"
curl -s -X PATCH http://localhost:8000/v1/communities/<id>/memberships/<user_id> -H "Authorization: Bearer $ADMIN" \
  -H 'Content-Type: application/json' -d '{"status":"approved"}'
curl -s -o /dev/null -w '%{http_code}\n' "http://localhost:8000/v1/communities/<id>/memberships" -H "Authorization: Bearer $MIEMBRO"  # 403
docker compose --env-file .env -f infra/docker-compose.yml run --rm api pytest
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] Ningún endpoint comprueba roles fuera de `CommunityAccess`.
- [ ] `docs/api` documenta el campo `status` del `403` y del `409`; `redocly lint` pasa y el *bundle* está regenerado.
- [ ] `pytest` y `ruff check` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Campo `status` en el `403`:** extensión compatible del contrato (solo añade un campo); se documenta en este ticket (§3.4).
- **Moderadores y listado:** el contrato permite que un `moderator` liste membresías; se respeta aunque el MVP no asigne ese rol.
- **Revisión irreversible:** un rechazo por error no se puede deshacer en el MVP (ver TK-015 §8).
