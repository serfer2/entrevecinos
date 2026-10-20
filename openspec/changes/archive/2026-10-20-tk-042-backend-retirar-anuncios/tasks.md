## 1. Base de datos

- [x] 1.1 Migración `0006` (`hidden_by`, `hidden_at`) y modelo

## 2. Moderación

- [x] 2.1 `ChangeListingStatus` con transiciones de moderación y `ListingRepository.set_status`
- [x] 2.2 `PATCH /v1/listings/{id}/status` y 409 `ListingStatusConflict`

## 3. Pruebas y verificación

- [x] 3.1 Integración de extremo a extremo (listado, búsqueda, detalle), permisos y reversibilidad; verificación TK-042 §6
