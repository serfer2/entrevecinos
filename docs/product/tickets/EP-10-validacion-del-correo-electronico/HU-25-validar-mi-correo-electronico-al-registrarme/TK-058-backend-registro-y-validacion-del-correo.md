# TK-058 · Backend: registro con validación del correo (`POST /v1/auth/register`, `POST /v1/auth/email-verification`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `users`, envío de correo), `docs/api/` |
| **Historia** | HU-25 Validar mi correo electrónico al registrarme (Épica 10) |
| **Prioridad** | Alta |
| **Depende de** | TK-006, TK-008, TK-056, TK-057 |
| **Referencias** | `docs/api/paths/auth_register.yaml`, `auth_token.yaml`; esquemas `AuthResponse`, `User` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Hoy `POST /auth/register` crea la cuenta activa y devuelve un JWT. HU-25 pide que la cuenta quede inactiva hasta que el usuario visite un enlace que recibe por correo, válido 24 horas.

**Objetivo:** registrar cuentas inactivas, enviar el correo de validación, exponer la validación del token (que activa la cuenta e inicia la sesión) e impedir el inicio de sesión de las cuentas sin validar, salvo `platform_admin`.

## 2. Alcance

**Incluye**
- Puerto `EmailSender` y adaptador SMTP (biblioteca estándar `smtplib`/`email`).
- Puerto `EmailVerificationRepository` y su implementación SQLAlchemy.
- Cambios en `RegisterUser`, nuevo caso de uso `VerifyEmail` y regla en `AuthenticateUser`.
- Endpoint `POST /auth/email-verification` y cambio de la respuesta de `POST /auth/register`.
- Contrato y tabla de cambios de `docs/api/README.md`.

**No incluye**
- El reenvío y el `409` de correo pendiente al registrarse (TK-059).
- Limpieza periódica de tokens caducados (asumido: se borran al reenviar o al validar).

## 3. Requisitos técnicos

### 3.1 Envío de correo

- `EmailSender.send(to, subject, text, html)`; adaptador `SmtpEmailSender` con la configuración de TK-056.
- El correo se envía **después** de confirmar la transacción, con `BackgroundTasks` de FastAPI: un fallo del SMTP no deshace el registro, se registra en el log y el usuario puede pedir otro correo (TK-059).
- Plantilla en español, texto y HTML: saludo con `full_name`, enlace `{WEB_PUBLIC_URL}/verificar-correo?token={token}`, aviso de caducidad en 24 horas y de que, si no ha sido él, puede ignorar el mensaje.
- En las pruebas, un `FakeEmailSender` en memoria guarda los correos (como `InMemoryObjectStorage`).

### 3.2 Token

- `secrets.token_urlsafe(32)`; se guarda solo su SHA-256 (`token_hash`) con `expires_at = now + EMAIL_VERIFICATION_TTL_HOURS`.
- Crear un token borra los anteriores del usuario: solo el último enlace es válido.

### 3.3 `POST /v1/auth/register`

- Crea la cuenta con `is_active = false` y `email_verified_at = null`, crea el token y envía el correo.
- Respuesta `201` con el esquema nuevo `RegistrationResponse`: `{"email": "...", "verification_expires_at": "..."}`. **Ya no devuelve un JWT**: cambio incompatible del contrato (lo usa solo la web, TK-060).
- Correo de una cuenta ya validada → `409` como hasta ahora («El correo ya está en uso.»).

### 3.4 `POST /v1/auth/email-verification`

- Público (`security: []`). Cuerpo `{"token": "..."}` (`extra="forbid"`).
- Token válido y sin caducar → activa la cuenta (`is_active = true`, `email_verified_at = now`), borra sus tokens y responde `200` con `AuthResponse` (JWT), para que la web inicie la sesión como hacía el registro.
- Token caducado → `410` `{"detail": "El enlace de validación ha caducado.", "code": "verification_expired", "email": "..."}`; se devuelve el correo para ofrecer el reenvío sin pedirlo (asumido: quien tiene el token recibió el correo).
- Token desconocido (nunca existió, ya usado o sustituido por uno más reciente) → `400` `{"detail": "El enlace de validación no es válido.", "code": "verification_invalid"}`.
- Esquema nuevo `EmailVerificationRequest`; respuesta de error `VerificationError` (`Error` + `code` + `email` opcional).

### 3.5 Inicio de sesión y usuario actual

- `User.email_verified_at`; `can_authenticate` exige `is_active` y `deleted_at` nulo, como ahora.
- `AuthenticateUser`: con la contraseña correcta, una cuenta sin validar y sin rol `platform_admin` → `EmailNotVerified` → `403` `{"detail": "Tienes que validar tu correo electrónico antes de iniciar sesión.", "code": "email_not_verified"}` (asumido, HU-25 AC4). Solo se revela tras comprobar la contraseña, así que no expone qué correos existen.
- Una cuenta desactivada por otros motivos sigue respondiendo `401` genérico.
- `GET /users/me` no cambia (la cuenta de un token válido ya está validada).

### 3.6 Pruebas

- Registro: cuenta inactiva, token guardado con hash, un correo en el *fake* con el enlace, respuesta sin JWT.
- Validación: token válido (activa y devuelve JWT), caducado (`410` con correo), usado o sustituido (`400`), cuerpo inválido (`422`).
- Inicio de sesión: sin validar → `403`; `platform_admin` sin validar → `200`; validado → `200`.
- El *helper* `register` de las pruebas valida la cuenta (con el token del *fake*) para que el resto de pruebas sigan trabajando con cuentas activas.

## 4. Criterios de aceptación

**AC1 — Registro (HU-25 AC1)**
- **Given** un correo no registrado
- **When** se hace `POST /v1/auth/register` con datos válidos
- **Then** se recibe `201` con `email` y `verification_expires_at`, sin token, la cuenta queda inactiva y Mailpit recibe el correo con el enlace

**AC2 — Validación (HU-25 AC2)**
- **Given** un token emitido hace menos de 24 horas
- **When** se hace `POST /v1/auth/email-verification`
- **Then** se recibe `200` con un JWT y la cuenta queda activa y validada

**AC3 — Caducado (HU-25 AC3)**
- **Given** un token emitido hace más de 24 horas
- **When** se valida
- **Then** se recibe `410` con `code: verification_expired` y el correo, y la cuenta sigue inactiva

**AC4 — Inicio de sesión sin validar (HU-25 AC4 y AC5)**
- **Given** una cuenta sin validar
- **When** inicia sesión con la contraseña correcta
- **Then** recibe `403` con `code: email_not_verified`, salvo si es `platform_admin`, que recibe `200`

## 5. Plan de tareas

1. `EmailSender`, `SmtpEmailSender`, plantilla y `FakeEmailSender`.
2. `EmailVerificationRepository` y generación del token.
3. `RegisterUser`, `VerifyEmail` y regla en `AuthenticateUser`.
4. Endpoints, errores y esquemas.
5. Contrato y `docs/api/README.md`.
6. Pruebas y *helper* `register`.
7. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
# POST /v1/auth/register → 201 sin token; correo en http://localhost:8025
# POST /v1/auth/email-verification con el token del enlace → 200 con JWT
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] Las pruebas de la API, `ruff` y `redocly lint` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Escáneres de enlaces del correo:** algunos clientes abren los enlaces para analizarlos. La validación no se hace con un `GET` a la API, sino desde la web (TK-060), que la trata como idempotente para el usuario: si el token ya se usó y la cuenta está validada, le pide iniciar sesión en lugar de mostrar un error (ver TK-060 §3.2).
- **Cambio incompatible en `registerUser`:** cualquier cliente que esperase el JWT tras registrarse deja de recibirlo.
