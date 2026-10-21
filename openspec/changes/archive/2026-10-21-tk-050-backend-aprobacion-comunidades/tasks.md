## 1. Dominio y persistencia

- [x] 1.1 `CommunityRepository.add(..., is_active)`, `list_all` y `activate` (puerto, SQLAlchemy y *fake*)
- [x] 1.2 `CreateCommunity` crea comunidades pendientes
- [x] 1.3 Casos de uso `ListAllCommunities` y `ApproveCommunity` (solo `platform_admin`)

## 2. API y contrato

- [x] 2.1 Router `admin` con `GET /admin/communities` y `PATCH /admin/communities/{id}`
- [x] 2.2 Contrato (`x-mvp: true`, descripciones) y `docs/api/README.md`

## 3. Verificación

- [x] 3.1 Pruebas (creación pendiente, listado, aprobación, 403, 404, 422) y *helper* `create_community`
- [x] 3.2 `pytest`, `ruff` y `redocly lint`
