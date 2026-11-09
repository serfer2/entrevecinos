# TK-106 · Backend: aviso por correo a la administración de cada solicitud de acceso

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad (con documentación) |
| **Componente** | `apps/api/` (área `communities`, correo, cupo), `docs/api/`, `infra/aws/README.md`, `apps/api/README.md` |
| **Historia** | HU-43 Recibir un aviso por correo de las solicitudes de acceso (Épica 8) |
| **Prioridad** | Media |
| **Depende de** | TK-015, TK-017, TK-058, TK-099 |
| **Referencias** | `application/communities/request_membership.py`; `presentation/v1/communities.py` (`request_membership`); `presentation/v1/auth.py` (`send_in_background`); `application/mail/email_quota.py`; `review_membership.py` (`COMMUNITY_ADMINS`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

`POST /v1/communities/{community_id}/memberships` crea una membresía `pending`, pero nadie se entera: la administración solo la ve si entra en la gestión de solicitudes. En producción ya ha ocurrido (2026-11-08): una solicitud quedó pendiente sin que el administrador lo supiera.

**Objetivo:** al crear una solicitud, enviar un correo a cada administrador aprobado de la comunidad con el nombre del solicitante y un enlace a las solicitudes pendientes, sin que un fallo del correo o la falta de cupo impidan la solicitud.

## 2. Alcance

**Incluye**
- Consulta de los destinatarios: miembros `approved` con rol `community_admin` de la comunidad, con la cuenta activa y no borrada.
- Plantilla del correo y su envío en segundo plano, reutilizables por TK-108.
- Cupo de correos: una plaza por destinatario.
- Descripción de `requestMembership` en el contrato (sin cambios de esquema).
- Documentación: el cupo cuenta estos avisos (`infra/aws/README.md`, `apps/api/README.md`).

**No incluye**
- Avisar al solicitante cuando se aprueba su solicitud (TK-108, HU-44).
- Preferencias para desactivar los avisos.
- Notificaciones dentro de la aplicación (versión futura).
- El texto que ve el solicitante (TK-107).

## 3. Requisitos técnicos

### 3.1 Destinatarios

- Nuevo método en el puerto `MembershipRepository`: `list_admin_recipients(community_id) -> list[User]` (asumido el nombre): membresías `approved` con rol `community_admin`, usuario `is_active` y `deleted_at` nulo.
- Solo `community_admin`: son los únicos que pueden aprobar (`COMMUNITY_ADMINS` en `ChangeMembershipStatus`). Los moderadores y los `platform_admin` sin membresía de administrador no reciben nada (asumido).
- El solicitante nunca se avisa a sí mismo (no puede ser administrador de una comunidad en la que pide entrar).

### 3.2 Mensaje

- Asunto: «Nueva solicitud para unirse a {comunidad}».
- Texto y HTML (con `escape`): saludo con el nombre del administrador, «{solicitante} ha pedido unirse a {comunidad}.», enlace `{WEB_PUBLIC_URL}/comunidades/{community_id}/gestion/solicitudes` y «Recibes este correo porque administras {comunidad} en EntreVecinos.».
- Sin el correo ni el teléfono del solicitante (HU-43 AC3).
- Un correo por destinatario: ningún administrador ve las direcciones de los demás (HU-43 AC2).

### 3.3 Caso de uso y envío

- `MembershipNotices.request_received(community, requester)` (`application/communities/membership_notices.py`) prepara un aviso por destinatario y reserva una plaza del cupo para cada uno con `EmailQuota.reserve()`. `RequestMembership` no cambia; el endpoint llama a los dos. TK-108 añadirá a `MembershipNotices` el aviso de aprobación.
- Sin cupo (`EmailQuotaExceeded`): la solicitud se crea igual y no se envían más avisos; queda en el registro como en TK-099 (HU-43 AC4).
- El endpoint envía los avisos con `BackgroundTasks` después de confirmar la transacción, con `send_in_background`, que pasa de la autenticación a `presentation/v1/mail.py` para compartirlo. Un fallo del SMTP solo deja «No se pudo enviar el correo…» en el registro, que dispara la alarma `email-send-failures`.
- La respuesta de `requestMembership` no cambia (`201` con `Membership`; `409` si ya existe).

### 3.4 Contrato y documentación

- `docs/api/paths/communities_community_id_memberships.yaml`: la descripción del `POST` indica que se avisa por correo a los administradores y que consume cupo; tabla de cambios de `docs/api/README.md`.
- `infra/aws/README.md`: los avisos de solicitudes cuentan para el cupo de 5.000 (límites del correo, decisión del cupo y *runbook* de `email-quota-80`).
- `apps/api/README.md`: la descripción de `EMAIL_MONTHLY_LIMIT`.

### 3.5 Pruebas

- Unitarias: un aviso por administrador aprobado; ni miembros, ni moderadores, ni administradores pendientes, bloqueados, inactivos o borrados; mensaje sin correo ni teléfono del solicitante y con el enlace; una plaza por destinatario; sin cupo, solicitud creada y sin avisos.
- `db`: la consulta de destinatarios.
- Endpoint: `201` y un correo por administrador en el *fake*; `409` sin correos; sin cupo, `201` y sin correos.

## 4. Criterios de aceptación

**AC1 — Aviso (HU-43 AC1)**
- **Given** una comunidad con un administrador aprobado
- **When** un vecino hace `POST /v1/communities/{id}/memberships`
- **Then** se recibe `201` y Mailpit recibe «Nueva solicitud para unirse a {comunidad}» con el nombre del solicitante y el enlace a las solicitudes

**AC2 — Destinatarios (HU-43 AC2 y AC3)**
- **Given** una comunidad con dos administradores y un moderador
- **When** llega una solicitud
- **Then** se envían dos correos, uno a cada administrador, sin el correo ni el teléfono del solicitante

**AC3 — Sin cupo (HU-43 AC4)**
- **Given** el cupo de correos agotado
- **When** un vecino solicita unirse
- **Then** se recibe `201`, la solicitud queda pendiente y no se envía ningún aviso

**AC4 — Solicitud repetida**
- **Given** una solicitud ya existente
- **When** se repite
- **Then** se recibe `409` y no se envía ningún aviso

## 5. Plan de tareas

1. `list_admin_recipients` en el puerto, el repositorio SQLAlchemy y el *fake*.
2. Plantilla del aviso y cambios en `RequestMembership` (avisos y cupo).
3. `send_in_background` compartido y envío desde el endpoint.
4. Contrato, `docs/api/README.md`, `apps/api/README.md` e `infra/aws/README.md`.
5. Pruebas.
6. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
# Con una cuenta, solicitar unirse a una comunidad de otra → correo en http://localhost:8025
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Las pruebas de la API, `ruff` y `redocly lint` pasan.
- [x] Contrato, `apps/api/README.md` e `infra/aws/README.md` actualizados.
- [x] Cambios revisados y fusionados mediante *pull request* (PR #43 y #44).
- [x] Comprobado en producción con una solicitud real (2026-11-09).

## 8. Riesgos y decisiones abiertas

- **Abuso:** una persona solo puede tener una solicitud por comunidad (`409` si se repite), así que no puede inundar de avisos a una misma administración; solo tras una expulsión puede volver a pedir acceso. Pedir acceso a muchas comunidades sí genera un aviso por cada una; lo frenan el límite general del proxy y el cupo mensual, que avisa al 80 %.
- **Coste:** cada aviso gasta una plaza del cupo de 5.000 (un correo por administrador). Con el tráfico actual es despreciable.
- **Aviso al solicitante:** el aviso al vecino cuando se aprueba su solicitud es TK-108 (HU-44); reutiliza la plantilla y el envío de este ticket. El rechazo no se avisa.
