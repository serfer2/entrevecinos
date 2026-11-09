## Why

HU-45 (Épica 8): la API ya permite al `platform_admin` nombrar o quitar administradores (TK-109), pero la web no ofrece la acción y las filas de administradores no tienen botones. Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-45-nombrar-a-los-administradores-de-una-comunidad/TK-110-frontend-nombrar-y-quitar-administradores.md`.

## What Changes

- En «Gestionar comunidad» → «Miembros», solo para el `platform_admin`: «Nombrar administrador» en los miembros aprobados que no lo son y «Quitar administrador» en los administradores aprobados (incluido uno mismo), con confirmación.
- Mensajes «<nombre> ha sido nombrado administrador.» y «<nombre> ya no es administrador.»; el `409` de miembro no aprobado muestra «Solo se puede cambiar el rol de un miembro aprobado.».
- Para `community_admin` y el resto, la página no cambia.
- Documentación del rol en `docs/product/user-stories.md` y `readme.md`.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `web-community-admin`: «Gestión de miembros» incluye nombrar y quitar administradores para el `platform_admin`.

## Impact

- Web: `features/communities/admin/members.ts` (`MEMBER_ACTIONS`, `rowActions`, `MEMBER_CONFLICTS`), `actions.ts` (`manageMember`), `app/(privado)/comunidades/[communityId]/gestion/miembros/page.tsx`; pruebas junto al código.
- Docs: `docs/product/user-stories.md` (Roles), `readme.md` (§1.2 y MVP).
- Sin cambios de contrato, migraciones ni infraestructura.
