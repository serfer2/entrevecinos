## 1. Backend

- [x] 1.1 `CommunityNotPending` (dominio) y manejador `409`
- [x] 1.2 `CommunityRepository.delete_pending` (puerto, SQLAlchemy con `FOR UPDATE` y *fake*)
- [x] 1.3 `RejectCommunity` y `DELETE /v1/admin/communities/{community_id}`, con pruebas unitarias y de endpoint

## 2. Documentación

- [x] 2.1 Contrato (`adminRejectCommunity`), «Cambios» y resumen de `docs/api/README.md`; `redocly lint`
- [x] 2.2 `readme.md` (§1.2, MVP y §3.2) y `apps/api/README.md`

## 3. Verificación

- [x] 3.1 Suite completa de la API, `ruff check` y `ruff format --check`; ticket marcado
