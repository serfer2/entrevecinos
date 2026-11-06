## Why

HU-34: `x-mvp` no coincide con la API. El contrato marca 33 operaciones como MVP, pero la API implementa 27; las 6 restantes (`deleteCurrentUser`, `listMyListings`, `createCategory`, `updateCategory`, `updateCommunity`, `deleteMedia`) no las usa ninguna historia del MVP. Ticket: `docs/product/tickets/EP-12-documentacion-tecnica/HU-34-distinguir-que-parte-del-modelo-de-datos-y-de-la-api-pertenece-al-mvp/TK-074-docs-alcance-del-mvp-en-el-contrato-de-la-api.md`.

## What Changes

- `x-mvp: false` y descripción «**Versión futura:** no implementada en el MVP.» en esas 6 operaciones y en el resto de las futuras.
- `openapi.yaml`: `x-mvp` significa «implementada en el MVP»; *tags* enteramente futuros marcados «(versión futura)».
- `docs/api/README.md`: convención `x-mvp`, resumen dividido en «MVP (implementado)» y «Versiones futuras», fila TK-074 en «Cambios».

## Capabilities

### New Capabilities
- `api-contract`: alcance del MVP en el contrato de la API.

### Modified Capabilities

## Impact

- `docs/api/` (`openapi.yaml`, `paths/*.yaml`, `README.md`). Sin cambios de esquemas, rutas ni respuestas; sin cambios de código.
