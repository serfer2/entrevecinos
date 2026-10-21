# TK-059 · Backend: correo pendiente al registrarse y reenvío (`POST /v1/auth/email-verification/resend`)

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `users`), `docs/api/` |
| **Historia** | HU-26 Recibir de nuevo el correo de validación (Épica 10) |
| **Prioridad** | Alta |
| **Depende de** | TK-058 |
| **Referencias** | `docs/api/paths/auth_register.yaml`; `components/responses/Conflict.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Con TK-058, registrarse de nuevo con un correo pendiente de validación respondería «El correo ya está en uso.», sin salida para el usuario. HU-26 pide un error específico y poder recibir de nuevo el mensaje.

**Objetivo:** distinguir el correo pendiente en el registro y exponer el reenvío del correo de validación.

## 2. Alcance

**Incluye**
- `409` con `code: email_pending_verification` en `POST /auth/register`.
- Endpoint público `POST /auth/email-verification/resend`.
- Contrato y `docs/api/README.md`.

**No incluye**
- Cambiar el correo de una cuenta pendiente (sin historia; asumido).
- Un límite de envíos por IP: solo se limita por cuenta (§3.2).

## 3. Requisitos técnicos

### 3.1 Registro con un correo pendiente

- Cuenta existente con `email_verified_at` nulo y sin rol `platform_admin` → `409` `{"detail": "Este correo está pendiente de validación.", "code": "email_pending_verification"}`. No crea otra cuenta ni cambia la existente (los datos del segundo intento se descartan; asumido).
- Cuenta validada → `409` `{"detail": "El correo ya está en uso.", "code": "email_in_use"}` (se añade `code` para que la web distinga los casos).
- Esquema de error `RegistrationConflict` (`Error` + `code`).

### 3.2 `POST /v1/auth/email-verification/resend`

- Público. Cuerpo `{"email": "..."}` (`extra="forbid"`, formato de correo).
- Responde **siempre** `202` `{"detail": "Si el correo está pendiente de validación, te enviaremos un enlace nuevo."}`, exista o no la cuenta, para no revelar qué correos están registrados (HU-26 AC3).
- Si la cuenta existe y está pendiente: crea un token nuevo con caducidad de 24 horas, borra los anteriores (TK-058 §3.2) y envía el correo tras la respuesta.
- Límite: si el último token del usuario se creó hace menos de 60 segundos, no se envía otro (asumido); la respuesta sigue siendo `202`.

### 3.3 Pruebas

- Registro con correo pendiente → `409 email_pending_verification`, sin cambios; con correo validado → `409 email_in_use`.
- Reenvío: cuenta pendiente (correo nuevo, el token anterior deja de valer), correo inexistente, cuenta validada y reenvío antes de 60 segundos (todos `202`, sin correo en los tres últimos).
- El enlace reenviado caduca a las 24 horas.

## 4. Criterios de aceptación

**AC1 — Registro con un correo pendiente (HU-26 AC1)**
- **Given** una cuenta pendiente de validación
- **When** se registra otra vez con su correo
- **Then** se recibe `409` con `code: email_pending_verification`

**AC2 — Reenvío (HU-26 AC2)**
- **Given** una cuenta pendiente
- **When** se hace `POST /v1/auth/email-verification/resend` con su correo
- **Then** se recibe `202`, llega un correo nuevo válido 24 horas y el enlace anterior responde `400`

**AC3 — Sin revelar cuentas (HU-26 AC3)**
- **Given** un correo inexistente o ya validado
- **When** se pide el reenvío
- **Then** se recibe el mismo `202` y no se envía nada

## 5. Plan de tareas

1. `code` en los `409` del registro.
2. Caso de uso `ResendEmailVerification` con el límite de 60 segundos.
3. Endpoint, esquemas, contrato y `docs/api/README.md`.
4. Pruebas y verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
# Registrar dos veces el mismo correo sin validar → 409 email_pending_verification
# POST /v1/auth/email-verification/resend → 202 y correo nuevo en http://localhost:8025
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] Las pruebas de la API, `ruff` y `redocly lint` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Enumeración en el registro:** el `409` del registro ya revela si un correo existe (también antes de esta épica); el reenvío no añade esa información.
- **Cuentas pendientes indefinidamente:** una cuenta que nunca se valida ocupa su correo para siempre; borrar las pendientes antiguas quedaría para otra historia.
