# TK-060 · Frontend: aviso tras el registro y validación desde el enlace

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/auth`, `/registro`, `/verificar-correo`, `/iniciar-sesion`) |
| **Historia** | HU-25 Validar mi correo electrónico al registrarme (Épica 10) |
| **Prioridad** | Alta |
| **Depende de** | TK-007, TK-009, TK-048, TK-058 |
| **Referencias** | `user-stories.md` HU-25 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Con TK-058, el registro ya no devuelve un JWT: la cuenta se activa al validar el correo. Hoy `signup` crea la sesión y redirige a `/comunidades` (TK-048).

**Objetivo:** mostrar el aviso del correo enviado, atender el enlace de validación (activar, iniciar la sesión y llevar a `/comunidades`) y explicar en el inicio de sesión que falta validar el correo.

## 2. Alcance

**Incluye**
- `signup`: aviso en lugar de crear la sesión.
- Ruta `/verificar-correo` (pública) que valida el token, crea la sesión y redirige.
- Página de error de la validación (caducado o no válido).
- `login`: mensaje para `403 email_not_verified`.

**No incluye**
- El botón de reenvío en el registro, la página de error y el inicio de sesión (TK-061); aquí se dejan preparados los huecos.

## 3. Requisitos técnicos

### 3.1 Registro

- `signup`: con `201`, devuelve el estado `{ verificationSentTo: email }` y no crea sesión.
- `SignupForm` con ese estado sustituye el formulario por un aviso `role="status"`: «Te hemos enviado un correo a {email}. Abre el enlace que contiene para activar tu cuenta. El enlace caduca en 24 horas.», más «Si no lo ves, revisa la carpeta de correo no deseado.».

### 3.2 `/verificar-correo`

- *Route handler* `app/verificar-correo/route.ts` (`GET`), añadido a `PUBLIC_ROUTES`; las páginas de servidor no pueden escribir *cookies*.
- Sin `token` → `/verificar-correo/error?motivo=invalido`.
- `POST /v1/auth/email-verification`:
  - `200` → `createSession(...)` y redirección a `/comunidades` (como el registro antes de la validación, TK-048).
  - `410` → `/verificar-correo/error?motivo=caducado&email=<correo>`.
  - `400` → si hay una sesión válida, `/comunidades`; si no, `/iniciar-sesion?motivo=correo-validado` con «Tu correo ya está validado. Inicia sesión.» (asumido: cubre el enlace abierto dos veces o por un escáner de correo, TK-058 §8).
  - Red o `5xx` → `/verificar-correo/error?motivo=error`.
- La respuesta lleva `Referrer-Policy: no-referrer` y no se guarda en caché, para que el token no se filtre.

### 3.3 Página `/verificar-correo/error` (pública)

- `caducado`: «El enlace de validación ha caducado.» y el hueco del reenvío (TK-061).
- `invalido`: «El enlace de validación no es válido.» y enlace a `/iniciar-sesion`.
- `error`: «No hemos podido validar tu correo. Inténtalo de nuevo más tarde.».

### 3.4 Inicio de sesión

- `login`: `403` con `code: email_not_verified` → `formError` «Tienes que validar tu correo electrónico antes de iniciar sesión.», conservando el correo, y el hueco del reenvío (TK-061).
- `/iniciar-sesion?motivo=correo-validado` muestra su aviso como `motivo=sesion-caducada`.

### 3.5 Pruebas

- `signup`: `201` → estado con el correo, sin `createSession`.
- *Route handler*: `200`, `410`, `400` con y sin sesión, error y sin token.
- `login`: `403 email_not_verified`.
- `SignupForm`: aviso con el correo.

## 4. Criterios de aceptación

**AC1 — Aviso (HU-25 AC1)**
- **Given** un visitante en `/registro`
- **When** se registra con datos válidos
- **Then** ve «Te hemos enviado un correo a {email}…» y no entra en la aplicación

**AC2 — Validación (HU-25 AC2)**
- **Given** el correo de validación en Mailpit
- **When** abre el enlace
- **Then** llega a `/comunidades` con la sesión iniciada

**AC3 — Caducado (HU-25 AC3)**
- **Given** un enlace caducado
- **When** lo abre
- **Then** ve «El enlace de validación ha caducado.» y sigue sin sesión

**AC4 — Inicio de sesión sin validar (HU-25 AC4)**
- **Given** una cuenta sin validar
- **When** inicia sesión con la contraseña correcta
- **Then** ve «Tienes que validar tu correo electrónico antes de iniciar sesión.»

**AC5 — Enlace repetido**
- **Given** un enlace ya usado
- **When** lo vuelve a abrir sin sesión
- **Then** llega a `/iniciar-sesion` con «Tu correo ya está validado. Inicia sesión.»

## 5. Plan de tareas

1. `signup` y aviso en `SignupForm`.
2. *Route handler* `/verificar-correo` y página de error.
3. `403` en `login` y aviso `correo-validado`.
4. Pruebas y verificación según la sección 6.

## 6. Verificación

```bash
make dev
# /registro → aviso; http://localhost:8025 → abrir el enlace → /comunidades con sesión
# Volver a abrir el enlace tras cerrar sesión → /iniciar-sesion con «Tu correo ya está validado»
# Iniciar sesión con otra cuenta sin validar → mensaje de validación pendiente
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Correo en la URL de error:** el correo viaja en la *query* de la página de error para ofrecer el reenvío; no es un secreto, pero queda en el historial del navegador.
