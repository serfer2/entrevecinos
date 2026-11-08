## Why

HU-43 (Épica 8): una solicitud de acceso queda pendiente sin que la administración de la comunidad se entere; en producción ya ocurrió el 2026-11-08. Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-43-recibir-un-aviso-por-correo-de-las-solicitudes-de-acceso/TK-106-backend-aviso-por-correo-de-las-solicitudes-de-acceso.md`.

## What Changes

- **Aviso por correo** «Nueva solicitud para unirse a {comunidad}» a cada `community_admin` aprobado, activo y no borrado, al crear una solicitud con `POST /v1/communities/{community_id}/memberships`: nombre del solicitante, comunidad y enlace a `/comunidades/{id}/gestion/solicitudes`; sin correo ni teléfono del solicitante.
- **Un correo por destinatario** y una plaza del cupo por correo; sin cupo, la solicitud se crea igual y no se envían más avisos.
- **Envío en segundo plano** tras confirmar la transacción; la respuesta no cambia.
- **`send_in_background` compartido** entre autenticación y comunidades.
- **Contrato:** descripción de `requestMembership`; tabla de cambios de `docs/api/README.md`.
- **Documentación del cupo:** `infra/aws/README.md` y `apps/api/README.md`.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `community-access-requests`: aviso por correo a la administración al recibir una solicitud.

## Impact

- API: puerto `MembershipRepository` (`list_admin_recipients`), repositorio SQLAlchemy, nuevo `MembershipNotices` en `application/communities`, endpoint `request_membership`, módulo compartido de envío en `presentation/v1`; pruebas.
- Contrato: descripción del `POST` de membresías.
- Documentación: `infra/aws/README.md` y `apps/api/README.md` (sin cambios de infraestructura).
