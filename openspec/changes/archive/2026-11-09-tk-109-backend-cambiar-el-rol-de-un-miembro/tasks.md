## 1. Dominio y aplicación

- [x] 1.1 `MembershipChangeRejected.ONLY_APPROVED` («Solo se puede cambiar el rol de un miembro aprobado.»)
- [x] 1.2 Puerto `MembershipRepository.set_role` y parámetro `lock` de `count_admins`
- [x] 1.3 Caso de uso `ChangeMembershipRole` (solo `platform_admin`, solo aprobados, último administrador, idempotente)

## 2. Infraestructura y presentación

- [x] 2.1 `SqlAlchemyMembershipRepository.set_role` y `count_admins(lock=True)` con `FOR UPDATE`
- [x] 2.2 `MembershipUpdateRequest`: `status` o `role` (exactamente uno; `member` o `community_admin`)
- [x] 2.3 `update_membership` despacha `role` → `ChangeMembershipRole`; descripción sin la nota «Pendiente»

## 3. Contrato

- [x] 3.1 `communities_community_id_memberships_user_id.yaml` (descripción, ejemplo de `role`, `409`) y `MembershipUpdate.yaml`
- [x] 3.2 Fila TK-109 en «Cambios» de `docs/api/README.md`; `redocly lint`

## 4. Pruebas y verificación

- [x] 4.1 Unitarias de `ChangeMembershipRole` con *fakes*
- [x] 4.2 Endpoint (`@pytest.mark.db`): nombrar, quitar, último administrador, no aprobados, `403` de `community_admin`, `422` (ambos campos, `moderator`), nuevo administrador en `list_admin_recipients`
- [x] 4.3 Suite completa, `ruff check` y `ruff format --check`; marcar el ticket como implementado
