## Why

HU-31: la API deja pasar siempre a un `platform_admin` (`require_member`, `require_role`), pero la web decide qué mostrar solo por la membresía: un administrador sin membresía aprobada ve «Solicitar acceso» y no ve los anuncios. Ticket: `docs/product/tickets/EP-11-experiencia-de-usuario/HU-31-acceder-como-administrador-de-plataforma-a-cualquier-comunidad/TK-070-frontend-acceso-del-administrador-de-plataforma.md`.

## What Changes

- `canAccessCommunity` y `canManageCommunity` en `features/communities/access.ts`.
- Página de la comunidad y de publicar anuncio con esas reglas.
- `MembershipAction` con `isPlatformAdmin`: siempre «Entrar».

## Capabilities

### New Capabilities

### Modified Capabilities
- `web-communities`: «Entrar» y acceso a la comunidad para `platform_admin`.
- `web-listings`: listado y publicación para `platform_admin`.
- `web-community-admin`: «Gestionar comunidad» para `platform_admin`.

## Impact

- `apps/web` (`features/communities/`, `app/(privado)/comunidades/`).
