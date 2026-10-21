## 1. Base de datos

- [x] 1.1 Migración `0007` e índice en `CommunityModel`, con prueba de reversibilidad

## 2. Creación

- [x] 2.1 `has_pending`, `PendingCommunityExists` y comprobación en `CreateCommunity`
- [x] 2.2 Traducción del `IntegrityError` en `add` y manejador `409`
- [x] 2.3 Contrato y `docs/api/README.md`

## 3. Verificación

- [x] 3.1 Pruebas (caso de uso, API y BD), `pytest`, `ruff`, `redocly lint` y migración aplicada en desarrollo
