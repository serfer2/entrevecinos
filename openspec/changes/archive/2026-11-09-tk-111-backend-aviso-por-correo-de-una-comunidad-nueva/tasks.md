## 1. Backend

- [x] 1.1 `UserRepository.list_platform_admins` (puerto, SQLAlchemy y *fake*)
- [x] 1.2 `CommunityNotices.community_created` y su plantilla, con pruebas unitarias
- [x] 1.3 `CommunityNoticesDep` y envío desde `create_community`, con pruebas de endpoint

## 2. Documentación

- [x] 2.1 Contrato (`createCommunity`) y «Cambios» de `docs/api/README.md`; `redocly lint`
- [x] 2.2 `readme.md` (§1.2, MVP y §3.2), `apps/api/README.md`, `infra/aws/README.md` (cupo) y `docs/product/user-stories.md` («Fuera de alcance»)

## 3. Verificación

- [x] 3.1 Suite completa de la API, `ruff check` y `ruff format --check`; correo comprobado en Mailpit; ticket marcado
