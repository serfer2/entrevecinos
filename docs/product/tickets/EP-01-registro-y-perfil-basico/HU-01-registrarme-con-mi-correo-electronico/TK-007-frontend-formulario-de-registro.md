# TK-007 · Frontend: formulario de registro y sesión

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/auth/`, `lib/api/`, `app/registro/`) |
| **Historia** | HU-01 Registrarme con mi correo electrónico (Épica 1) |
| **Prioridad** | Alta |
| **Depende de** | TK-003, TK-006 |
| **Referencias** | `user-stories.md` HU-01; `docs/api/paths/auth_register.yaml`; `readme.md` §2.5 (JWT); guía de autenticación de Next 16 (`node_modules/next/dist/docs/01-app/02-guides/authentication.md`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El frontend solo tiene la página marcador de TK-003. HU-01 necesita un formulario de registro que muestre los errores junto a cada campo y que, al terminar, deje al vecino dentro de la aplicación con la sesión iniciada.

**Objetivo:** crear la página `/registro`, el cliente de la API para el servidor de Next, la gestión de la sesión con una *cookie* `httpOnly` y la primera página privada `/inicio` (marcador). También se configura la base de pruebas del frontend.

## 2. Alcance

**Incluye**
- Cliente de la API para el servidor (`lib/api/server.ts`).
- Esquema de validación del registro, *Server Action* `signup` y gestión de la *cookie* de sesión.
- Página `/registro` con el formulario (`SignupForm`).
- Página marcador `/inicio`, a la que se redirige tras registrarse.
- Dependencias `zod` y `server-only`, y pruebas con Vitest y Testing Library.

**No incluye**
- Inicio de sesión, protección de rutas y lectura del usuario actual (TK-009).
- Cierre de sesión (fuera de alcance según `user-stories.md`).
- Diseño visual definitivo: estilos funcionales con Tailwind, accesibles y responsive.

## 3. Requisitos técnicos

### 3.1 Decisión: sesión en *cookie* `httpOnly` gestionada por Next (asumido)

El navegador nunca recibe el JWT en JavaScript:

1. El formulario envía los datos a una *Server Action*.
2. La *Server Action* llama a la API (`API_INTERNAL_URL`) desde el servidor de Next.
3. Con la respuesta `201`, guarda `access_token` en la *cookie* `ev_session`.
4. Las siguientes llamadas a la API se hacen desde el servidor de Next (Server Components y Actions), leyendo la *cookie* y enviando `Authorization: Bearer <token>`.

Opciones de la *cookie*: `httpOnly: true`, `sameSite: "lax"`, `secure: NODE_ENV === "production"`, `path: "/"` y `maxAge: expires_in`.

**Alternativa descartada:** guardar el token en `localStorage` y llamar a la API desde el navegador. Expone el token a cualquier XSS.

### 3.2 Estructura de ficheros

```
apps/web/src/
├── lib/api/
│   ├── server.ts          # import "server-only"; apiFetch(path, init) → ApiResult
│   └── errors.ts          # ApiError { status, detail }, parseo de 422 (loc → campo)
├── features/auth/
│   ├── schemas.ts         # signupSchema (zod), mismas reglas que RegisterRequest
│   ├── session.ts         # import "server-only"; createSession(token, expiresIn), SESSION_COOKIE
│   ├── actions.ts         # "use server"; signup(prevState, formData)
│   └── components/
│       └── SignupForm.tsx # "use client"; useActionState(signup)
└── app/
    ├── registro/page.tsx
    └── (privado)/inicio/page.tsx   # marcador: "Sesión iniciada"
```

### 3.3 Cliente de la API (`lib/api/server.ts`)

- Solo se usa en el servidor (`import "server-only"`). La URL base es `process.env.API_INTERNAL_URL`.
- `apiFetch<T>(path, { method, body, token })` envía JSON, añade `Authorization` si hay token y usa `cache: "no-store"`. Devuelve `{ ok: true, data }` o `{ ok: false, error: ApiError }`.
- Los errores de red y las respuestas `5xx` se convierten en `ApiError` con `status: 0` o `5xx`, sin lanzar excepciones hacia la interfaz.

### 3.4 Validación (`features/auth/schemas.ts`)

Mismas reglas que `RegisterRequest`, con mensajes en español:

| Campo | Regla | Mensaje |
|---|---|---|
| `full_name` | se recorta; de 1 a 120 caracteres | «Introduce tu nombre.» / «Máximo 120 caracteres.» |
| `email` | correo válido; máximo 320 | «Introduce un correo electrónico válido.» |
| `password` | de 12 a 128 caracteres | «La contraseña debe tener al menos 12 caracteres.» |
| `phone` | opcional; máximo 32 | «Máximo 32 caracteres.» |

La *Server Action* valida siempre en el servidor antes de llamar a la API. La validación del navegador (atributos `required`, `type="email"` y `minLength`) es solo una ayuda.

### 3.5 *Server Action* `signup`

Devuelve un estado `{ fieldErrors?: Record<campo, string>, formError?: string, values?: { full_name, email, phone } }`:

- Datos inválidos según el esquema: `fieldErrors` sin llamar a la API.
- `201`: `createSession()` y `redirect("/inicio")`.
- `409`: `fieldErrors.email = "Este correo ya está en uso."` (HU-01 AC2).
- `422`: se traduce cada `loc` (`["body", "<campo>"]`) al mensaje del campo correspondiente de §3.4.
- Error de red o `5xx`: `formError = "No se pudo crear la cuenta. Inténtalo de nuevo."`.
- Cuando hay error se devuelven los valores introducidos, **salvo la contraseña**, para no obligar a reescribirlos.

### 3.6 Formulario (`SignupForm`)

- Campos: nombre (`autocomplete="name"`), correo (`type="email"`, `autocomplete="email"`), contraseña (`type="password"`, `autocomplete="new-password"`, con la ayuda «Mínimo 12 caracteres») y teléfono opcional (`type="tel"`, `autocomplete="tel"`).
- Cada error aparece bajo su campo, enlazado con `aria-describedby` y con `aria-invalid="true"`. El error general se muestra con `role="alert"`.
- El botón se desactiva y muestra «Creando cuenta…» mientras `pending` es `true`.
- Enlace «¿Ya tienes cuenta? Inicia sesión» a `/iniciar-sesion` (la página se crea en TK-009).

### 3.7 Pruebas

- Dependencias de desarrollo: `vitest`, `@vitejs/plugin-react`, `jsdom`, `@testing-library/react`, `@testing-library/dom` y `vite-tsconfig-paths`. Script `"test": "vitest run"`.
- `schemas.test.ts`: casos válidos e inválidos de cada campo.
- `actions.test.ts`: `signup` con `apiFetch` y `cookies()` simulados, para `201` (crea la *cookie* y redirige), `409`, `422` y error de red.
- `SignupForm.test.tsx`: muestra los errores de campo y el error general, y conserva los valores salvo la contraseña.

## 4. Criterios de aceptación

**AC1 — Registro correcto (HU-01 AC1)**

- **Given** que no tengo cuenta y estoy en `/registro`
- **When** introduzco nombre, un correo no registrado y una contraseña de 12 o más caracteres, y envío el formulario
- **Then** se me redirige a `/inicio` y el navegador guarda la *cookie* `ev_session` con `HttpOnly` y `SameSite=Lax`, que no es accesible desde `document.cookie`

**AC2 — Correo ya registrado (HU-01 AC2)**

- **Given** que existe una cuenta con `vecino@example.com`
- **When** intento registrarme con ese correo
- **Then** veo «Este correo ya está en uso.» bajo el campo de correo, sigo en `/registro` con el nombre y el correo rellenos, y no se crea la *cookie*

**AC3 — Datos inválidos (HU-01 AC3)**

- **Given** que estoy en `/registro`
- **When** envío el formulario con el correo mal formado, el nombre vacío o una contraseña de menos de 12 caracteres (incluso con la validación del navegador desactivada)
- **Then** veo un mensaje junto a cada campo incorrecto y no se llama a la API

**AC4 — API no disponible**

- **Given** que la API no responde
- **When** envío un formulario válido
- **Then** veo un error general que puedo volver a intentar, y mis datos (salvo la contraseña) se conservan

**AC5 — Calidad**

- **Given** el código del frontend
- **When** ejecuto `npm run lint`, `npm run typecheck`, `npm run test` y `npm run build`
- **Then** todos terminan sin errores, y ningún componente de cliente importa `lib/api/server.ts` ni `features/auth/session.ts`

## 5. Plan de tareas

1. Añadir `zod`, `server-only` y las dependencias de pruebas; configurar `vitest.config.mts` y el script `test`.
2. Implementar `lib/api/server.ts` y `lib/api/errors.ts`.
3. Implementar `signupSchema` con sus pruebas.
4. Implementar `session.ts` y la *Server Action* `signup` con sus pruebas.
5. Implementar `SignupForm` y la página `/registro`, accesibles y responsive.
6. Crear la página marcador `/inicio` en el grupo `(privado)`.
7. Documentar la sesión y las pruebas en `apps/web/README.md`, y verificar según la sección 6.

## 6. Verificación

```bash
make dev
# Navegador: http://localhost:3000/registro
#   - registro correcto → /inicio; en DevTools > Application > Cookies: ev_session HttpOnly, SameSite=Lax
#   - document.cookie en la consola no muestra ev_session
#   - repetir con el mismo correo → error bajo el campo de correo
#   - desactivar la validación del navegador (atributo novalidate en DevTools) y enviar datos inválidos → errores por campo
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE stop api        # AC4: enviar el formulario → error general
$COMPOSE start api
$COMPOSE exec web npm run lint
$COMPOSE exec web npm run typecheck
$COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] El token nunca llega al JavaScript del navegador: no aparece en `NEXT_PUBLIC_*`, en *props* de componentes de cliente ni en `document.cookie`.
- [ ] El formulario se puede usar solo con teclado y en pantallas de móvil.
- [ ] `apps/web/README.md` explica el flujo de sesión y cómo ejecutar las pruebas.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **CSRF:** las *Server Actions* de Next comparan las cabeceras `Origin` y `Host` y solo aceptan `POST`. Con `SameSite=Lax` se considera suficiente para el MVP.
- **Caducidad de la sesión:** la *cookie* dura lo mismo que el token (`expires_in`). La gestión de un token caducado se cubre en TK-009.
- **Reglas duplicadas entre frontend y backend:** el esquema `zod` repite los límites de `RegisterRequest`. Si cambia el contrato hay que actualizar ambos. Se valorará generar tipos desde `docs/api` (`packages/api-contracts`, README §2.3).
- **`/inicio` sin protección todavía:** la protección de rutas llega en TK-009. Hasta entonces, `/inicio` solo muestra un marcador sin datos personales.
