# TK-108 · Backend: aviso por correo al solicitante cuando se aprueba su solicitud

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad (con documentación) |
| **Componente** | `apps/api/` (área `communities`, correo, cupo), `docs/api/`, `infra/aws/README.md` |
| **Historia** | HU-44 Recibir un aviso por correo cuando me aceptan en una comunidad (Épica 8) |
| **Prioridad** | Media |
| **Depende de** | TK-017, TK-040, TK-106 |
| **Referencias** | `application/communities/review_membership.py` (`ChangeMembershipStatus`); `presentation/v1/communities.py` (`update_membership`); plantilla y envío de TK-106 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Con TK-106, la administración se entera de cada solicitud. El vecino, en cambio, no sabe cuándo lo aprueban: tiene que volver a entrar para comprobarlo.

**Objetivo:** al aprobar una solicitud pendiente (`PATCH /v1/communities/{community_id}/memberships/{user_id}` de `pending` a `approved`), enviar un correo al solicitante con un enlace a la comunidad, sin que un fallo del correo o la falta de cupo impidan la aprobación.

## 2. Alcance

**Incluye**
- Aviso solo en la transición `pending → approved`, la apruebe un `community_admin` o un `platform_admin`.
- Plantilla del correo y envío en segundo plano, con el mismo mecanismo que TK-106.
- Cupo de correos: una plaza por aviso.
- Descripción de `updateMembership` en el contrato (sin cambios de esquema).
- Documentación del cupo en `infra/aws/README.md`.

**No incluye**
- Avisos al rechazar, bloquear, desbloquear o expulsar (HU-44 AC2).
- El texto de la web para el solicitante (TK-107).

## 3. Requisitos técnicos

### 3.1 Cuándo se avisa

- `ChangeMembershipStatus.execute` devuelve `MembershipChange` (la membresía y su estado anterior), con `approves_request` cierto solo si el estado anterior era `pending` y el nuevo `approved`; el endpoint pide entonces el aviso a `MembershipNotices.request_approved(community_id, user_id)`, que comprueba la comunidad y la cuenta y reserva el cupo. El desbloqueo (`blocked → approved`) no avisa (asumido: no es una aceptación nueva).
- El destinatario es el solicitante, con su cuenta activa y no borrada; si no, no se envía nada.

### 3.2 Mensaje

- Asunto: «Ya eres miembro de {comunidad}».
- Texto y HTML (con `escape`): saludo con el nombre del vecino, «Tu solicitud para unirte a {comunidad} ha sido aprobada. Ya puedes ver y publicar anuncios.» y enlace `{WEB_PUBLIC_URL}/comunidades/{community_id}`.
- Sin datos del administrador que la aprobó (asumido).

### 3.3 Cupo y envío

- Reserva una plaza con `EmailQuota.reserve()`; sin cupo (`EmailQuotaExceeded`), la aprobación se hace igual y no se envía el aviso, que queda en el registro como en TK-099 (HU-44 AC3).
- El endpoint lo envía con `BackgroundTasks` tras confirmar la transacción, con el `send_in_background` compartido de TK-106. Un fallo del SMTP dispara la alarma `email-send-failures`.
- La respuesta de `updateMembership` no cambia.

### 3.4 Contrato y documentación

- `docs/api/paths/communities_community_id_memberships_user_id.yaml`: la descripción del `PATCH` indica el aviso al aprobar una solicitud y su consumo de cupo; tabla de cambios de `docs/api/README.md`.
- `infra/aws/README.md`: los avisos de aprobación cuentan para el cupo de 5.000.

### 3.5 Pruebas

- Unitarias: aviso al aprobar una solicitud pendiente; sin aviso al rechazar, bloquear o desbloquear; sin aviso si la cuenta del solicitante está inactiva o borrada; una plaza del cupo; sin cupo, aprobación hecha y sin aviso.
- Endpoint: aprobación por `community_admin` y por `platform_admin` con un correo al solicitante en el *fake*; rechazo sin correo; sin cupo, `200` y sin correo.

## 4. Criterios de aceptación

**AC1 — Aviso de aprobación (HU-44 AC1)**
- **Given** una solicitud pendiente
- **When** un administrador la aprueba
- **Then** se recibe `200` y Mailpit recibe «Ya eres miembro de {comunidad}» dirigido al solicitante, con el enlace a la comunidad

**AC2 — Solo al aprobar (HU-44 AC2)**
- **Given** una membresía
- **When** se rechaza la solicitud, o se bloquea o desbloquea al miembro
- **Then** no se envía ningún correo

**AC3 — Sin cupo (HU-44 AC3)**
- **Given** el cupo de correos agotado
- **When** se aprueba una solicitud
- **Then** se recibe `200`, el vecino es miembro aprobado y no se envía el aviso

## 5. Plan de tareas

1. Plantilla del aviso y cambios en `ChangeMembershipStatus` (aviso y cupo).
2. Envío desde el endpoint.
3. Contrato, `docs/api/README.md` e `infra/aws/README.md`.
4. Pruebas.
5. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
# Aprobar una solicitud desde la gestión de la comunidad → correo al solicitante en http://localhost:8025
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Las pruebas de la API, `ruff` y `redocly lint` pasan.
- [x] Contrato e `infra/aws/README.md` actualizados.
- [x] Cambios revisados y fusionados mediante *pull request* (PR #43 y #44).
- [x] Comprobado en producción con una solicitud real (2026-11-09).

## 8. Riesgos y decisiones abiertas

- **Coste:** un correo por aprobación; cada solicitud gasta como mucho uno al aprobarse más uno por administrador al recibirla (TK-106).
- **Sin aviso de rechazo:** se evita comunicar un rechazo por correo; el vecino lo ve al entrar en la comunidad («No tienes acceso a esta comunidad.»). Si se quisiera avisar, sería otra historia.
