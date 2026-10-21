# TK-061 · Frontend: reenviar el correo de validación

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/auth`, `/registro`, `/verificar-correo/error`, `/iniciar-sesion`) |
| **Historia** | HU-26 Recibir de nuevo el correo de validación (Épica 10) |
| **Prioridad** | Alta |
| **Depende de** | TK-059, TK-060 |
| **Referencias** | `user-stories.md` HU-26 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

TK-059 expone el reenvío y distingue el correo pendiente en el registro. TK-060 dejó tres sitios donde el usuario necesita pedir otro correo: el registro con un correo pendiente, el enlace caducado y el inicio de sesión sin validar.

**Objetivo:** un único botón «Reenviar el correo de validación» en esos tres sitios.

## 2. Alcance

**Incluye**
- *Server Action* `resendVerification(formData)` y componente `ResendVerificationButton`.
- Uso en `/registro` (`409 email_pending_verification`), `/verificar-correo/error?motivo=caducado` y `/iniciar-sesion` (`403 email_not_verified`).

**No incluye**
- Una página independiente para pedir el reenvío escribiendo el correo (asumido: el correo siempre se conoce en los tres casos).

## 3. Requisitos técnicos

### 3.1 *Server Action* `resendVerification`

- Recibe `email` (campo oculto); `POST /v1/auth/email-verification/resend`.
- `202` → estado `{ sent: true }`; cualquier error → `{ error: "No se pudo reenviar el correo. Inténtalo de nuevo." }`.

### 3.2 `ResendVerificationButton`

- Componente cliente con `useActionState`: botón «Reenviar el correo de validación»; mientras se envía, «Enviando…» y deshabilitado.
- Tras `sent`: «Si tu cuenta está pendiente de validación, te hemos enviado un correo nuevo. Revisa tu bandeja de entrada.» (`role="status"`) y el botón se oculta (asumido: evita reenvíos en bucle; el límite real lo pone la API).

### 3.3 Integración

- **Registro:** `signup` con `409 email_pending_verification` → error bajo el correo «Este correo está pendiente de validación.» y el botón con ese correo. Con `email_in_use`, el mensaje de siempre.
- **Enlace caducado:** la página de error muestra el botón con el `email` de la URL; sin `email`, solo el enlace a `/registro`.
- **Inicio de sesión:** con `email_not_verified`, el botón bajo el mensaje, con el correo escrito.

### 3.4 Pruebas

- `resendVerification`: `202`, error.
- `ResendVerificationButton`: estado inicial, envío y aviso.
- `signup`: `409` con cada `code`.

## 4. Criterios de aceptación

**AC1 — Registro con un correo pendiente (HU-26 AC1)**
- **Given** una cuenta pendiente
- **When** el visitante se registra otra vez con ese correo
- **Then** ve «Este correo está pendiente de validación.» y el botón «Reenviar el correo de validación»

**AC2 — Reenvío (HU-26 AC2)**
- **Given** el botón en cualquiera de los tres sitios
- **When** lo pulsa
- **Then** ve el aviso de correo enviado y en Mailpit hay un correo nuevo cuyo enlace funciona; el anterior ya no

**AC3 — Sin revelar cuentas (HU-26 AC3)**
- **Given** un correo que no está pendiente
- **When** se pide el reenvío
- **Then** ve el mismo aviso

## 5. Plan de tareas

1. *Server Action* y componente, con pruebas.
2. Integración en registro, página de error e inicio de sesión.
3. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Registrar un correo, no validarlo y registrarlo otra vez → error + botón → correo nuevo en Mailpit
# Iniciar sesión con la cuenta sin validar → mensaje + botón
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- Ninguno relevante.
