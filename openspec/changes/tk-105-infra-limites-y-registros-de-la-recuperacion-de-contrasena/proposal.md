## Why

HU-41 AC5 (Épica 14): sin WAF, el proxy nginx limita por IP los `POST` de `/iniciar-sesion` y `/registro`. Las páginas nuevas `/recuperar-contrasena` (envía correos) y `/restablecer-contrasena` (prueba *tokens*) quedan solo con el límite general. Además, el Compose de producción no fija la caducidad del enlace y la guía de producción no recoge la funcionalidad. Ticket: `docs/product/tickets/EP-14-recuperacion-de-la-contrasena/HU-41-pedir-un-enlace-para-restablecer-mi-contrasena/TK-105-infra-limites-y-registros-de-la-recuperacion-de-contrasena.md`.

## What Changes

- **Proxy:** `/recuperar-contrasena` y `/restablecer-contrasena` pasan al `location` con `zone=auth` (20 `POST` en 5 minutos por IP, compartidos con el inicio de sesión y el registro). `/restablecer-contrasena/enlace` solo atiende `GET` y sigue en el límite general.
- **Compose de producción:** `PASSWORD_RESET_TTL_MINUTES: "60"` explícito en la API.
- **Registros sin *token*:** el proxy ya registra `$uri` sin la cadena de consulta y CloudFront no registra `cs-uri-query` (TK-091); se comprueba en producción con un enlace real.
- **`infra/aws/README.md`:** rutas limitadas, los enlaces de restablecimiento y el aviso del cambio cuentan para el cupo de 5.000, *runbook* de las alarmas del cupo y del abuso del formulario, y comprobaciones.

## Capabilities

### New Capabilities
- (ninguna)

### Modified Capabilities
- `production-deployment`: el límite del proxy cubre también las rutas de recuperación de la contraseña.

## Impact

- `infra/prod/proxy/default.conf.template`, `infra/docker-compose.prod.yml` e `infra/aws/README.md`.
- Producción: el documento de SSM incrusta ambos ficheros, así que exige `make tf-apply` antes de desplegar.
