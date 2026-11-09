## Why

HU-46 (Épica 8): una comunidad nueva queda pendiente sin que nadie se entere; el administrador de plataforma solo la ve si entra en «Comunidades pendientes». Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-46-recibir-un-aviso-por-correo-cuando-alguien-crea-una-comunidad/TK-111-backend-aviso-por-correo-de-una-comunidad-nueva.md`.

## What Changes

- Al crear una comunidad pendiente (`POST /v1/communities` de un vecino), cada `platform_admin` con la cuenta activa recibe en segundo plano «Nueva comunidad pendiente: {comunidad}» con los datos de la comunidad (nombre, descripción, ciudad, código postal, fecha) y del creador (nombre, correo, teléfono, fecha de alta), y un enlace a `/admin/comunidades#comunidad-{id}`.
- Sin aviso cuando la crea un `platform_admin` (queda activa).
- Una plaza del cupo por correo; sin cupo, la comunidad se crea igual y no se avisa. La respuesta no cambia.
- **Contrato:** descripción de `createCommunity`; «Cambios» de `docs/api/README.md`. **Documentación:** `readme.md` (§1.2, MVP y §3.2), `apps/api/README.md`, `infra/aws/README.md` (cupo) y `docs/product/user-stories.md`.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `community-approval`: nuevo requisito «Aviso por correo de una comunidad nueva».

## Impact

- API: `UserRepository.list_platform_admins` (puerto, SQLAlchemy y *fake*), `CommunityNotices` (`application/communities/community_notices.py`), `CommunityNoticesDep`, endpoint `create_community`; pruebas.
- Documentación: contrato, `docs/api/README.md`, `readme.md`, `apps/api/README.md`, `infra/aws/README.md` (sección del cupo de correos), `docs/product/user-stories.md`.
- Sin migraciones. `infra/aws/README.md` cambia solo en la documentación del cupo; ninguna ruta de infraestructura cambia.
