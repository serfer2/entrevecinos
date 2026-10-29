## Why

HU-34: el modelo de datos de `readme.md` §3 describe 15 entidades sin distinguir las 8 del MVP (con tabla) de las 7 previstas para versiones futuras, y no las relaciona con la API. Ticket: `docs/product/tickets/EP-12-documentacion-tecnica/HU-34-distinguir-que-parte-del-modelo-de-datos-y-de-la-api-pertenece-al-mvp/TK-075-docs-alcance-del-mvp-en-el-modelo-de-datos.md`.

## What Changes

- §3.1: «Versión futura» en las entidades futuras del diagrama ER y nota con el reparto.
- §3.2: tabla «Entidad | Alcance | Rutas de la API»; encabezados, enumerados e índices de las entidades futuras marcados «(versión futura)».
- §1.2 y §4: remiten a las entidades y operaciones futuras y explican `x-mvp`.
- `docs/product/user-stories.md` («Fuera de alcance»): remite al modelo de datos y al contrato.

## Capabilities

### New Capabilities

### Modified Capabilities

Ninguna: solo documentación.

## Impact

- `readme.md`, `docs/product/user-stories.md`. Sin cambios de código ni de esquema.
