## 1. Backend

- [x] 1.1 `list_admin_recipients` en el puerto, el repositorio SQLAlchemy y el *fake*, con prueba `db`
- [x] 1.2 `MembershipNotices.request_received` (destinatarios, cupo y plantilla), con pruebas unitarias
- [x] 1.3 `send_in_background` compartido y avisos desde el endpoint `request_membership`, con pruebas de endpoint

## 2. Contrato y documentación

- [x] 2.1 Descripción de `requestMembership` y tabla de cambios de `docs/api/README.md`; lint
- [x] 2.2 `infra/aws/README.md` y `apps/api/README.md` (el cupo cuenta los avisos)

## 3. Verificación

- [x] 3.1 `make ci-api` y prueba local con Mailpit
