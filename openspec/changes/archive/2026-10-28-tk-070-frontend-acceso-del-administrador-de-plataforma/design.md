## Context

`CommunityAccess.require_member` y `require_role` de la API ya aceptan a un `platform_admin`.

## Decisions

- **Reglas en un único módulo** (`access.ts`), con pruebas: `canAccessCommunity` (membresía `approved` o `platform_admin`) y `canManageCommunity` (`community_admin` aprobado o `platform_admin`).
- **Ocultar acciones no protege nada:** la API sigue decidiendo los permisos.
- **Selector de comunidad sin cambios:** sigue listando solo las membresías aprobadas.

## Risks / Trade-offs

- [Sus anuncios no aparecían en el listado] → TK-071.
