## 1. Paginación y migración

- [x] 1.1 `application/pagination.py` y `presentation/v1/pagination.py`
- [x] 1.2 Migración `0003` (`unaccent`, `f_unaccent`)

## 2. Búsqueda y solicitudes

- [x] 2.1 `CommunityRepository.search` y `SearchCommunities`; `GET /v1/communities`
- [x] 2.2 Dominio de membresías, `MembershipRepository`, `RequestMembership` y `ListMyMemberships`
- [x] 2.3 `POST /v1/communities/{id}/memberships` (409 con `status`) y `GET /v1/users/me/memberships`

## 3. Pruebas y verificación

- [x] 3.1 Unitarias de los casos de uso; integración AC1–AC4 (incluida la carrera por la PK)
- [x] 3.2 Documentar la paginación en `apps/api/README.md` y verificación TK-015 §6
