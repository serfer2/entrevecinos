# TK-103 · Frontend: «¿Has olvidado tu contraseña?» y formulario para pedir el enlace

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/auth`, `/iniciar-sesion`, `/recuperar-contrasena`) |
| **Historia** | HU-41 Pedir un enlace para restablecer mi contraseña (Épica 14) |
| **Prioridad** | Alta |
| **Depende de** | TK-009, TK-067, TK-099, TK-101 |
| **Referencias** | `app/iniciar-sesion/page.tsx`; `features/auth/components/LoginForm.tsx`; `features/auth/actions.ts` (`resendVerification`, `isEmailQuotaExceeded`); `features/auth/routes.ts` (`PUBLIC_ROUTES`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La pantalla de inicio de sesión no ofrece ninguna salida a quien ha olvidado su contraseña. TK-101 expone `POST /v1/auth/password-reset`.

**Objetivo:** añadir el enlace «¿Has olvidado tu contraseña?» al inicio de sesión y una página pública donde pedir el enlace por correo, con un mensaje que no revela si el correo tiene cuenta.

## 2. Alcance

**Incluye**
- Enlace en `LoginForm`.
- Página `/recuperar-contrasena` con su formulario y Server Action `requestPasswordReset`.
- Ruta en `PUBLIC_ROUTES`.

**No incluye**
- La página para elegir la contraseña nueva (TK-104).
- Los límites por IP del proxy para la ruta nueva (TK-105).

## 3. Requisitos técnicos

### 3.1 Inicio de sesión

- `LoginForm`: enlace «¿Has olvidado tu contraseña?» junto al campo de contraseña, a `/recuperar-contrasena`. Tras un intento fallido, el correo escrito se pasa como `?email=` para rellenar el formulario (asumido: el formulario no es controlado y es justo cuando el usuario descubre que no recuerda la contraseña).
- Estilo del tema actual (TK-066/TK-067), accesible con teclado y con texto visible (no solo un icono).

### 3.2 `/recuperar-contrasena`

- Página pública con `AuthShell`: título «Recupera tu contraseña» e introducción «Escribe el correo de tu cuenta y te enviaremos un enlace para elegir una contraseña nueva.».
- Formulario con un campo de correo (validación con zod, mismos mensajes que el inicio de sesión) y botón «Enviar enlace».
- Server Action `requestPasswordReset` (en `features/auth/actions.ts`, solo exporta funciones `async`):
  - `202` → el formulario se sustituye por un aviso `role="status"`: «Si hay una cuenta con ese correo, te hemos enviado un enlace para restablecer la contraseña. Caduca en 1 hora. Si no lo ves, revisa la carpeta de correo no deseado.», y enlace «Volver a iniciar sesión».
  - `503 email_quota_exceeded` → «Ahora mismo no podemos enviar correos. Inténtalo de nuevo en unos días.», conservando el correo (el mensaje del registro habla de «correos de validación»).
  - `422` → error junto al campo.
  - `429`, red o `5xx` → «No hemos podido enviar el enlace. Inténtalo de nuevo en unos minutos.».
- Con sesión iniciada, redirige a `/inicio`, como `/iniciar-sesion`.
- `metadata.title`: «Recuperar contraseña · EntreVecinos».

### 3.3 Pruebas

- `LoginForm`: muestra el enlace y lo construye con el correo escrito.
- `requestPasswordReset`: `202`, `503`, `422` y error de red.
- Formulario: aviso tras el envío, sin revelar si el correo existe.
- `isPublicRoute("/recuperar-contrasena")`.

## 4. Criterios de aceptación

**AC1 — Enlace visible (HU-41 AC1)**
- **Given** un visitante en `/iniciar-sesion`
- **When** mira el formulario
- **Then** ve «¿Has olvidado tu contraseña?» y, al pulsarlo, llega a `/recuperar-contrasena`

**AC2 — Mismo mensaje para cualquier correo (HU-41 AC3)**
- **Given** el formulario de `/recuperar-contrasena`
- **When** envía un correo con cuenta o sin ella
- **Then** ve el mismo aviso y, solo en el primer caso, Mailpit recibe el correo

**AC3 — Sin cupo (HU-40 AC5)**
- **Given** el cupo de correos agotado
- **When** pide el enlace
- **Then** ve el mensaje de que ahora no se pueden enviar correos y su correo sigue escrito

## 5. Plan de tareas

1. Enlace en `LoginForm`.
2. Server Action `requestPasswordReset` y esquema zod.
3. Página y formulario de `/recuperar-contrasena`; ruta pública.
4. Pruebas.
5. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
# http://localhost:3000/iniciar-sesion → «¿Has olvidado tu contraseña?» → enviar → correo en http://localhost:8025
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Lint, tipos y pruebas de la web pasan.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Correo en la URL:** `?email=` solo rellena el formulario y no se envía a la API sin que el usuario pulse el botón. El proxy y CloudFront no registran la cadena de consulta (TK-091).
