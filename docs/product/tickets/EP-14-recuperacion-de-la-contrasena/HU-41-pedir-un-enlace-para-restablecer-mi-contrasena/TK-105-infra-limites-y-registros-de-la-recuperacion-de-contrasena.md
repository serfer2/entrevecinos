# TK-105 · Infra: límites por IP y registros sin *token* en la recuperación de contraseña

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura |
| **Componente** | `infra/prod/proxy/default.conf.template`, `infra/docker-compose.prod.yml`, `infra/aws/README.md` |
| **Historia** | HU-41 Pedir un enlace para restablecer mi contraseña (Épica 14); también sirve a HU-42 |
| **Prioridad** | Alta |
| **Depende de** | TK-087, TK-091, TK-101, TK-103, TK-104 |
| **Referencias** | `infra/prod/proxy/default.conf.template` (`zone=auth`, `log_format origin`); `infra/aws/modules/edge/` (campos del registro de CloudFront) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Sin WAF, el proxy nginx limita por IP los `POST` de `/iniciar-sesion` y `/registro` (20 en 5 minutos). Las páginas nuevas `/recuperar-contrasena` y `/restablecer-contrasena` envían correos o prueban *tokens*, así que necesitan el mismo límite. El enlace del correo lleva el *token* en la cadena de consulta.

**Objetivo:** aplicar el límite de autenticación a las rutas nuevas, comprobar que ningún registro guarda el *token* y documentar la funcionalidad en la guía de producción.

## 2. Alcance

**Incluye**
- Rutas nuevas en el `location` con `zone=auth` del proxy.
- `PASSWORD_RESET_TTL_MINUTES` en el Compose de producción.
- Comprobación de que el proxy y CloudFront no registran `?token=`.
- `infra/aws/README.md`: límites, correos que consumen cupo y *runbook*.

**No incluye**
- Alarmas nuevas: los fallos de envío y el cupo ya avisan (`email-send-failures`, `email-quota-80`, `email-quota-exceeded`).

## 3. Requisitos técnicos

- `location ~ ^/(iniciar-sesion|registro|recuperar-contrasena|restablecer-contrasena)$` con `zone=auth` (los `GET` no cuentan, como hoy). `/restablecer-contrasena/enlace` solo atiende `GET` y queda en el límite general.
- El `log_format origin` ya registra `$uri` sin la cadena de consulta, y CloudFront no registra `cs-uri-query` (TK-091): verificarlo en producción con un enlace real.
- Compose de producción: `PASSWORD_RESET_TTL_MINUTES: "60"`.
- `make tf-apply` antes de desplegar, porque el documento de SSM incrusta `infra/prod/` y el Compose.

## 4. Criterios de aceptación

**AC1 — Límite por IP (HU-41 AC5)**
- **Given** producción
- **When** una IP hace más de 20 `POST` a `/recuperar-contrasena` en 5 minutos
- **Then** recibe `429` y no se envían más correos

**AC2 — Sin *token* en los registros**
- **Given** un enlace de restablecimiento abierto en producción
- **When** se buscan los registros del proxy (`/entrevecinos/prod/proxy`) y de CloudFront
- **Then** aparece `/restablecer-contrasena/enlace` sin `token=`

**AC3 — Documentado**
- **Given** `infra/aws/README.md`
- **When** consulto los límites y el correo de producción
- **Then** encuentro las rutas limitadas, que los enlaces de restablecimiento cuentan para el cupo de 5.000 y qué hacer si alguien abusa del formulario

## 5. Plan de tareas

1. `location` del proxy y variable del Compose.
2. `make shellcheck`, `make tf-lint`, `make tf-plan` y, con confirmación, `make tf-apply`.
3. Prueba del límite y de los registros tras desplegar.
4. `infra/aws/README.md`.

## 6. Verificación

```bash
make tf-lint && make shellcheck
make tf-plan   # cambia el documento de SSM
for i in $(seq 1 25); do curl -s -o /dev/null -w '%{http_code}\n' -X POST https://entrevecinos.org/recuperar-contrasena; done
# los últimos responden 429
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] `make tf-lint` y `make shellcheck` pasan; cambio aplicado y desplegado.
- [x] `infra/aws/README.md` actualizado.
- [x] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Zona compartida:** el inicio de sesión, el registro y la recuperación comparten la zona `auth`; quien abuse de una ruta también se bloquea en las otras durante unos minutos. Se acepta: es el mismo tipo de abuso.
