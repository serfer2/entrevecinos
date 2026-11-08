# TK-101 · Backend: solicitar el restablecimiento de la contraseña (`POST /v1/auth/password-reset`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `users`, correo, cupo), `docs/api/` |
| **Historia** | HU-41 Pedir un enlace para restablecer mi contraseña (Épica 14) |
| **Prioridad** | Alta |
| **Depende de** | TK-058, TK-059, TK-099, TK-100 |
| **Referencias** | `application/users/email_verification.py` (`EmailVerificationIssuer`, `hash_token`); `resend_email_verification.py` (`RESEND_MIN_INTERVAL`, cupo antes de buscar la cuenta); `presentation/v1/auth.py` (`send_in_background`); `docs/api/paths/auth_email_verification_resend.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Quien olvida su contraseña no tiene forma de recuperar su cuenta. La API ya sabe enviar enlaces de un solo uso por correo (validación, TK-058) con un cupo mensual (TK-099).

**Objetivo:** un endpoint público que, dado un correo, envía un enlace para elegir una contraseña nueva, sin revelar si el correo tiene cuenta y sin permitir abusos.

## 2. Alcance

**Incluye**
- Puerto `PasswordResetRepository` y su implementación SQLAlchemy.
- `PasswordResetIssuer` (crea el enlace y el mensaje) y caso de uso `RequestPasswordReset`.
- Endpoint `POST /v1/auth/password-reset`.
- Ajuste `PASSWORD_RESET_TTL_MINUTES` (60) en `Settings` y `.env.example` (el Compose de producción, en TK-105).
- Contrato (`x-mvp: true`) y tabla de cambios de `docs/api/README.md`; extracto del `readme.md` regenerado.

**No incluye**
- El cambio de la contraseña con el enlace (TK-102).
- La interfaz (TK-103) y los límites por IP del proxy (TK-105).

## 3. Requisitos técnicos

### 3.1 Enlace

- `secrets.token_urlsafe(32)`; se guarda solo su SHA-256 (reutilizar `hash_token`) con `expires_at = now + PASSWORD_RESET_TTL_MINUTES`.
- Crear un enlace borra los anteriores del usuario: solo vale el último (HU-41 AC4).
- Enlace: `{WEB_PUBLIC_URL}/restablecer-contrasena/enlace?token={token}` (lo atiende la web en TK-104).
- Mensaje en español, texto y HTML (con `escape` como el de validación): asunto «Restablece tu contraseña de EntreVecinos», saludo con `full_name`, enlace, caducidad en 60 minutos y «Si no lo has pedido tú, ignora este mensaje: tu contraseña no cambiará.».

### 3.2 `RequestPasswordReset`

En este orden:
1. `quota.ensure_available()` **antes de buscar la cuenta**: sin cupo, `EmailQuotaExceeded` (`503`) para cualquier correo, como el reenvío (TK-099).
2. Busca la cuenta por correo normalizado. No hace nada (sin error) si no existe, si está borrada (`deleted_at`) o si está desactivada con el correo ya validado (asumido: bloqueada por otros motivos).
3. Cuenta sin validar (`email_verification_pending`): sí recibe el enlace; al usarlo quedará validada (HU-42 AC5, TK-102).
4. Si el último enlace del usuario tiene menos de 60 segundos, no hace nada (HU-41 AC5).
5. `quota.reserve()` y emite el enlace.

Devuelve el mensaje a enviar o `None`; el llamante no distingue los casos.

### 3.3 `POST /v1/auth/password-reset`

- Público (`security: []`). Cuerpo `{"email": "..."}` (`extra="forbid"`, formato de correo).
- Siempre `202` con `{"detail": "Si hay una cuenta con ese correo, te enviaremos un enlace para restablecer la contraseña."}`, exista o no la cuenta (HU-41 AC3), con la misma forma que el reenvío del correo de validación. El correo se envía con `BackgroundTasks` después de confirmar la transacción (`send_in_background`), así que el tiempo de respuesta no depende de si se envía.
- Sin cupo → `503` `email_quota_exceeded` con `Retry-After`.
- Cuerpo inválido → `422`.
- Los registros no incluyen el correo pedido ni el *token*.

### 3.4 Contrato

- `docs/api/paths/auth_password_reset.yaml`, operación `requestPasswordReset` con `x-mvp: true`; esquemas `PasswordResetRequest` y `PasswordResetRequested`.
- `test_contract_scope.py` sigue pasando: la ruta existe y está marcada como MVP.

### 3.5 Pruebas

- Cuenta activa: `202`, un correo en el *fake* con el enlace y un enlace guardado con hash.
- Correo sin cuenta, cuenta borrada y cuenta desactivada validada: `202` y ningún correo.
- Cuenta sin validar: `202` y correo.
- Dos peticiones seguidas: un solo correo; tras 60 segundos (reloj inyectado), otro, y el primero deja de valer.
- Sin cupo: `503` tanto con correo registrado como sin registrar.
- Cada envío consume una plaza del cupo.

## 4. Criterios de aceptación

**AC1 — Enlace enviado (HU-41 AC2)**
- **Given** una cuenta activa
- **When** se hace `POST /v1/auth/password-reset` con su correo
- **Then** se recibe `202` y Mailpit recibe el correo con un enlace válido 60 minutos

**AC2 — Sin revelar cuentas (HU-41 AC3)**
- **Given** un correo sin cuenta
- **When** se pide el enlace
- **Then** se recibe la misma respuesta `202` y no se envía nada

**AC3 — Solo el último y uno por minuto (HU-41 AC4 y AC5)**
- **Given** un enlace pedido hace menos de 60 segundos
- **When** se pide otro
- **Then** no se envía; pasado el minuto, se envía uno nuevo y el anterior deja de valer

**AC4 — Cupo (HU-40 AC5)**
- **Given** el cupo de correos agotado
- **When** se pide el enlace con cualquier correo
- **Then** se recibe `503` con `code: email_quota_exceeded` y `Retry-After`

## 5. Plan de tareas

1. `PasswordResetRepository` (puerto e implementación).
2. `PasswordResetIssuer` y plantilla del correo.
3. `RequestPasswordReset` y ajuste `PASSWORD_RESET_TTL_MINUTES`.
4. Endpoint, esquema y dependencias.
5. Contrato, `docs/api/README.md` y extracto del `readme.md`.
6. Pruebas.
7. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
curl -i -X POST localhost:8000/v1/auth/password-reset -H 'Content-Type: application/json' \
  -d '{"email":"vecino@example.com"}'   # 202; correo en http://localhost:8025
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Las pruebas de la API, `ruff` y `redocly lint` pasan.
- [x] Contrato, `.env.example` y `apps/api/README.md` actualizados.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Bombardeo de correos a terceros:** alguien podría pedir enlaces para correos ajenos. Lo frenan el límite de uno por minuto por cuenta, el límite por IP del proxy (TK-105) y el cupo mensual, que además avisa al 80 %.
- **Consumo del cupo:** un abuso sostenido podría agotar el cupo y bloquear también los registros hasta el día 6. Se acepta mientras el tráfico sea bajo; si ocurre, la alarma `email-quota-80` avisa antes.
- **Tiempo de respuesta:** buscar la cuenta tarda algo más cuando existe. La diferencia es de milisegundos y la tapa la latencia de red; no se añade espera artificial (asumido).
