## Why

HU-22: un `platform_admin` no debería tener que aprobar sus propias comunidades. Ticket: `docs/product/tickets/EP-08-mejora-de-la-gestion-de-comunidades/HU-22-activar-al-momento-las-comunidades-que-crea-un-administrador-de-plataforma/TK-052-backend-comunidades-activas-para-platform-admin.md`.

## What Changes

- `POST /v1/communities` crea la comunidad activa cuando el creador es `platform_admin`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `community-management`: comunidades activas al momento para el `platform_admin`.

## Impact

- `apps/api` (`CreateCommunity`), `docs/api`. La web ya redirige a la comunidad cuando la respuesta trae `is_active: true` (TK-051).
