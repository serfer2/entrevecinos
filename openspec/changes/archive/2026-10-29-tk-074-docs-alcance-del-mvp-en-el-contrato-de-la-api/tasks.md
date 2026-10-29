## 1. Contrato

- [x] 1.1 `x-mvp: false` y «Versión futura» en `deleteCurrentUser`, `listMyListings`, `createCategory`, `updateCategory`, `updateCommunity` y `deleteMedia`
- [x] 1.2 «Versión futura» en la descripción del resto de operaciones `x-mvp: false`
- [x] 1.3 `info.description` (definición de `x-mvp`) y *tags* futuros de `openapi.yaml`

## 2. Documentación

- [x] 2.1 `docs/api/README.md`: convención `x-mvp`, resumen MVP / versiones futuras y fila TK-074 en «Cambios»

## 3. Verificación

- [x] 3.1 `redocly lint` y `bundle` sin errores
- [x] 3.2 27 operaciones `x-mvp: true`, iguales a las rutas de `presentation/v1/`
