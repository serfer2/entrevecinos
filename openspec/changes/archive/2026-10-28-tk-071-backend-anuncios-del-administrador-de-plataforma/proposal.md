## Why

HU-31 AC3: el listado solo muestra anuncios de autores con membresía aprobada (`OWNER_IS_MEMBER`, TK-040). Tras TK-070, un `platform_admin` puede publicar sin membresía aprobada y su anuncio no aparece, ni siquiera para él. Ticket: `docs/product/tickets/EP-11-experiencia-de-usuario/HU-31-acceder-como-administrador-de-plataforma-a-cualquier-comunidad/TK-071-backend-anuncios-del-administrador-de-plataforma.md`.

## What Changes

- `OWNER_IS_MEMBER`: membresía aprobada **o** autor `platform_admin`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `community-authorization`: un autor `platform_admin` cuenta como miembro aprobado.

## Impact

- `apps/api` (`infrastructure/listings/sqlalchemy_listing_repository.py`, `tests/`). Sin cambios de contrato.
