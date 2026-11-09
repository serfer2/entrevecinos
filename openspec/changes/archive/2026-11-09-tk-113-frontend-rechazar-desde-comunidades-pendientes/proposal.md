## Why

HU-47 (Épica 8): la API ya permite rechazar una comunidad pendiente (TK-112), pero «Comunidades pendientes» solo ofrece «Aprobar». El correo de TK-111 enlazará a esta página para aprobar o rechazar. Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-47-rechazar-una-comunidad-pendiente/TK-113-frontend-rechazar-desde-comunidades-pendientes.md`.

## What Changes

- Botón «Rechazar» con confirmación en cada comunidad de `/admin/comunidades`; *Server Action* `rejectCommunity` (`DELETE /admin/communities/{id}`).
- Mensajes: «Se ha rechazado la comunidad <nombre>.», «Esta comunidad ya está activa: no se puede rechazar.», «Esta comunidad ya no está pendiente.» y «No se pudo rechazar la comunidad. Inténtalo de nuevo.».
- Ancla `#comunidad-<id>` en cada fila para el enlace del correo.
- **Documentación:** `apps/web/README.md`.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `web-platform-admin`: nuevo requisito «Rechazar comunidades desde la interfaz».

## Impact

- Web: `features/platform-admin/` (`actions.ts`, `paths.ts`, pruebas), `app/(privado)/admin/comunidades/page.tsx`.
- Docs: `apps/web/README.md`. Sin cambios de contrato, migraciones ni infraestructura.
