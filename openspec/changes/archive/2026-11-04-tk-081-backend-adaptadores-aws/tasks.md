## 1. Backend

- [x] 1.1 `Settings`: almacenamiento opcional con validación de claves, región y estilo; `MAIL_BACKEND`, `SES_REGION` y `SES_CONFIGURATION_SET`; `SMTP_HOST` y STARTTLS solo con `smtp`; con pruebas
- [x] 1.2 `S3ObjectStorage` con credenciales por defecto, región y estilo de direccionamiento, con pruebas de la URL firmada
- [x] 1.3 `SesEmailSender` y selección en `get_email_sender`, con pruebas con `Stubber`

## 2. Documentación

- [x] 2.1 `.env.example`, `infra/docker-compose.yml` (`MAIL_BACKEND`) y tabla de configuración de `apps/api/README.md`

## 3. Verificación

- [x] 3.1 Suite completa de la API, `ruff check` y `ruff format --check` en contenedores
- [x] 3.2 `openspec validate tk-081-backend-adaptadores-aws`
