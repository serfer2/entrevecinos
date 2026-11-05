## Context

La API corre en local con MinIO y Mailpit y en producción correrá en una EC2 con rol IAM (TK-085). boto3 obtiene las credenciales del rol por IMDSv2 sin configuración.

## Goals / Non-Goals

**Goals:** mismo código en local y en AWS, eligiendo solo por variables de entorno; ninguna clave de larga duración en AWS.

**Non-Goals:** infraestructura de SES (TK-083, TK-084) y del rol (TK-085).

## Decisions

- **Cadena por defecto en lugar de claves:** si no hay `STORAGE_ACCESS_KEY`, no se pasan credenciales a `boto3.client`. Alternativa descartada: usuario IAM con claves en Parameter Store; añade una clave de larga duración que rotar.
- **API de SES en lugar de SMTP:** SMTP con SES exige un usuario IAM con clave de larga duración convertida en contraseña SMTP. `sesv2.send_email` usa el rol. SMTP se conserva para Mailpit.
- **Cadenas vacías como «no definido»** en `Settings`, coherentes con los valores vacíos de `.env`; `Literal` se sustituye por validadores con mensajes en español.
- **Un solo cliente cuando el endpoint público coincide** con el de subida (o no existe), en lugar de dos clientes idénticos.
- **Cliente de SES cacheado** con `lru_cache`, como el almacenamiento, porque crear clientes de boto3 es costoso.

## Risks / Trade-offs

- [Los contenedores solo obtienen las credenciales del rol si el *hop limit* de IMDSv2 es 2] → lo fija TK-085.
- [Un error de SES no se ve en la respuesta] → se registra como hoy los de SMTP (`send_in_background`), sin datos personales.
