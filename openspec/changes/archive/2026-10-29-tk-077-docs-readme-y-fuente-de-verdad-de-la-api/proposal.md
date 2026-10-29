## Why

HU-35: `readme.md` §4 incluye un OpenAPI propio, anterior al contrato de `docs/api/`, que no lo menciona y ya no coincide con él (p. ej. `/auth/register` aún devuelve un token, contra TK-058). Ticket: `docs/product/tickets/EP-12-documentacion-tecnica/HU-35-consultar-la-api-en-una-unica-fuente-de-verdad/TK-077-docs-readme-y-fuente-de-verdad-de-la-api.md`.

## What Changes

- §4 declara `docs/api/openapi.yaml` como fuente de verdad y enlaza `docs/api/README.md`.
- El fragmento pasa a ser un extracto del contrato *bundled* con `listCommunityListings`, `createListing`, `registerUser` y `loginUser` y los componentes que referencian, con el aviso «si difieren, prevalece el contrato».
- `docs/api/README.md`: comando para regenerar el extracto.

## Capabilities

### New Capabilities

### Modified Capabilities
- `api-contract`: fuente de verdad y extracto del README.

## Impact

- `readme.md` §4, `docs/api/README.md`. Sin cambios de código ni del contrato.
