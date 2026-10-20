# TK-009 · Frontend: inicio de sesión y protección de rutas

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad y seguridad |
| **Componente** | `apps/web/` (`features/auth/`, `app/iniciar-sesion/`, `app/(privado)/`, `src/proxy.ts`) |
| **Historia** | HU-02 Iniciar sesión (Épica 1) |
| **Prioridad** | Alta (bloquea todas las pantallas privadas) |
| **Depende de** | TK-007, TK-008 |
| **Referencias** | `user-stories.md` HU-02; `docs/api/paths/auth_token.yaml`, `users_me.yaml`; guía de autenticación de Next 16 (Proxy, *Data Access Layer*) y `03-api-reference/03-file-conventions/proxy.md` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

TK-007 dejó el registro, la *cookie* `ev_session` y la página marcador `/inicio`, pero sin protección. HU-02 pide iniciar sesión, mostrar un error genérico y exigir sesión antes de ver el contenido privado, como los anuncios de una comunidad.

**Objetivo:** crear la página `/iniciar-sesion` y proteger todas las rutas privadas en dos niveles: una comprobación rápida en `proxy.ts` y una verificación real contra la API en la capa de acceso a datos (DAL). La protección se aplica por defecto, así que las rutas futuras, como `/comunidades/[id]/anuncios`, quedan protegidas sin tocar nada.

## 2. Alcance

**Incluye**
- Esquema `loginSchema`, *Server Action* `login` y componente `LoginForm`.
- Página `/iniciar-sesion` con el parámetro `next`.
- `src/proxy.ts`, que redirige a `/iniciar-sesion` las rutas no públicas cuando no hay *cookie*.
- DAL `features/auth/dal.ts` con `getCurrentUser()` y `requireUser()`, que llaman a `GET /v1/users/me`.
- `/inicio` muestra «Hola, {nombre}» con `requireUser()`.
- Las páginas de registro e inicio de sesión redirigen a `/inicio` si la sesión ya es válida.

**No incluye**
- Cierre de sesión y recuperación de contraseña (fuera de alcance según `user-stories.md`).
- Páginas de comunidades y anuncios (Épicas 2 a 4): solo se garantiza que quedarán protegidas.
- Página de perfil (TK-011).

## 3. Requisitos técnicos

### 3.1 Estructura de ficheros

```
apps/web/src/
├── proxy.ts                         # comprobación rápida en cada petición
├── features/auth/
│   ├── schemas.ts                   # + loginSchema
│   ├── actions.ts                   # + login(prevState, formData)
│   ├── dal.ts                       # import "server-only"; getCurrentUser, requireUser
│   ├── redirect.ts                  # safeNextPath(value) → ruta interna segura
│   ├── routes.ts                    # PUBLIC_ROUTES, LOGIN_PATH, HOME_PATH
│   └── components/LoginForm.tsx     # "use client"; useActionState(login)
└── app/
    ├── iniciar-sesion/page.tsx
    └── (privado)/inicio/page.tsx    # usa requireUser()
```

### 3.2 Rutas públicas y privadas

- Públicas: `/`, `/registro` e `/iniciar-sesion` (`PUBLIC_ROUTES`).
- Privadas: **todas las demás**.
- `HOME_PATH = "/inicio"`: destino por defecto tras registrarse o iniciar sesión. TK-007 pasa a usar esta constante.

### 3.3 `src/proxy.ts`: comprobación rápida

- Exporta `proxy(request)` y un `config.matcher` que excluye `_next/static`, `_next/image`, `favicon.ico` y los ficheros con extensión (recursos de `public/`).
- Si la ruta no es pública y no existe la *cookie* `ev_session`, redirige a `/iniciar-sesion?next=<ruta + query>`.
- No valida el token ni llama a la API: según la guía de Next, el Proxy se ejecuta en cada petición, incluidas las de *prefetch*, y solo debe hacer comprobaciones rápidas.
- **No** redirige fuera de `/iniciar-sesion` a quien tiene *cookie*. Si la *cookie* contuviera un token caducado, eso provocaría un bucle de redirecciones (ver §3.4).

### 3.4 DAL: verificación real

- `getCurrentUser = cache(async () => …)` (`react`):
  - Sin *cookie*: devuelve `null`.
  - Llama a `GET /v1/users/me` con el token (`apiFetch` de TK-007).
  - `200`: devuelve un DTO `{ id, full_name, email, phone }`, solo con los campos que necesita la interfaz.
  - `401`: devuelve `null` (token caducado o usuario desactivado).
  - Otros errores: lanza un error y lo muestra el `error.tsx` del grupo `(privado)`.
- `requireUser()`: llama a `getCurrentUser()` y, si devuelve `null`, ejecuta `redirect("/iniciar-sesion?motivo=sesion-caducada")`.
- Cada página o acción privada llama a `requireUser()` cerca de los datos. **No** se confía solo en el *layout*: la guía de Next advierte que los *layouts* no se vuelven a renderizar al navegar.
- `/iniciar-sesion` y `/registro` llaman a `getCurrentUser()` y redirigen a `/inicio` solo si la sesión es válida. Así se evita el bucle de §3.3.

### 3.5 *Server Action* `login`

- Valida con `loginSchema` (correo válido y contraseña no vacía).
- `POST /v1/auth/token`:
  - `200`: `createSession()` y `redirect(safeNextPath(next) ?? HOME_PATH)`.
  - `401`: `formError = "Correo o contraseña incorrectos."` (HU-02 AC2). No se marca ningún campo concreto.
  - `422`: errores por campo, igual que en TK-007.
  - Error de red o `5xx`: `formError = "No se pudo iniciar sesión. Inténtalo de nuevo."`.
- Cuando hay error se conserva el correo y nunca la contraseña.

### 3.6 Redirección segura (`safeNextPath`)

- Acepta solo rutas internas: deben empezar por `/`, no por `//` ni `/\`, y no pueden contener `:` antes de la primera `/`. Cualquier otro valor se ignora y se usa `HOME_PATH`.
- Evita el *open redirect* (`/iniciar-sesion?next=https://malicioso.example`).

### 3.7 Página `/iniciar-sesion`

- Formulario con correo (`autocomplete="email"`) y contraseña (`autocomplete="current-password"`). Mismos patrones de accesibilidad que `SignupForm`.
- El campo oculto `next` se rellena con el parámetro de la URL.
- Si llega `motivo=sesion-caducada`, se muestra el aviso «Tu sesión ha caducado. Vuelve a iniciar sesión.».
- Enlace «¿No tienes cuenta? Regístrate» a `/registro`.

### 3.8 Pruebas

- `redirect.test.ts`: valores válidos (`/comunidades/1/anuncios?page=2`) e inválidos (`//evil.example`, `https://evil.example`, `/\evil`, `javascript:alert(1)`, cadena vacía).
- `proxy.test.ts`: con `NextRequest`, comprobar ruta pública sin *cookie* (pasa), ruta privada sin *cookie* (redirige con `next` codificado) y ruta privada con *cookie* (pasa).
- `actions.test.ts`: `login` con `200` (crea la *cookie* y redirige a `next`), `401` (error genérico), `next` malicioso (redirige a `/inicio`) y error de red.
- `dal.test.ts`: `getCurrentUser` con `200`, `401` y sin *cookie*.

## 4. Criterios de aceptación

**AC1 — Acceso correcto (HU-02 AC1)**

- **Given** que tengo una cuenta y estoy en `/iniciar-sesion`
- **When** introduzco mi correo y mi contraseña correctos
- **Then** se me redirige a `/inicio`, que muestra «Hola, {mi nombre}», y se guarda la *cookie* `ev_session` (`HttpOnly`, `SameSite=Lax`)

**AC2 — Credenciales incorrectas (HU-02 AC2)**

- **Given** que estoy en `/iniciar-sesion`
- **When** introduzco un correo no registrado o una contraseña incorrecta
- **Then** veo «Correo o contraseña incorrectos.» en los dos casos, sin indicar qué dato falló, y el correo sigue escrito

**AC3 — Contenido protegido (HU-02 AC3)**

- **Given** que no he iniciado sesión
- **When** abro `/inicio` o `/comunidades/123/anuncios`
- **Then** se me redirige a `/iniciar-sesion?next=…` y, tras iniciar sesión, vuelvo a la ruta que había pedido

**AC4 — Sesión caducada**

- **Given** que tengo una *cookie* `ev_session` con un token caducado o inválido
- **When** abro `/inicio`
- **Then** se me redirige a `/iniciar-sesion` con el aviso de sesión caducada, sin bucles de redirección, y puedo volver a iniciar sesión

**AC5 — Redirección segura**

- **Given** la URL `/iniciar-sesion?next=https://evil.example`
- **When** inicio sesión correctamente
- **Then** se me redirige a `/inicio` y no a un dominio externo

## 5. Plan de tareas

1. Definir `routes.ts` y `safeNextPath`, con sus pruebas, y hacer que TK-007 use `HOME_PATH`.
2. Implementar `src/proxy.ts` y sus pruebas.
3. Implementar el DAL (`getCurrentUser`, `requireUser`) y sus pruebas.
4. Implementar `loginSchema`, la *Server Action* `login` y sus pruebas.
5. Implementar `LoginForm` y la página `/iniciar-sesion`, con el aviso de sesión caducada.
6. Actualizar `/inicio` (saludo con `requireUser()`), añadir `error.tsx` en `(privado)` y la redirección de `/registro` e `/iniciar-sesion` con sesión válida.
7. Documentar en `apps/web/README.md` cómo crear una página privada, y verificar según la sección 6.

## 6. Verificación

```bash
make dev
# Navegador, sin sesión (ventana privada):
#   http://localhost:3000/inicio                      → /iniciar-sesion?next=%2Finicio
#   http://localhost:3000/comunidades/123/anuncios    → /iniciar-sesion?next=… ; tras iniciar sesión vuelve a esa ruta (404 por ahora)
#   credenciales incorrectas (correo inexistente o contraseña mal) → mismo mensaje
#   /iniciar-sesion?next=https://evil.example          → tras iniciar sesión, /inicio
# Sesión caducada: en DevTools, cambiar el valor de ev_session a "x" y recargar /inicio → aviso, sin bucle
curl -sI http://localhost:3000/inicio | grep -iE '^HTTP|location'   # 307 a /iniciar-sesion?next=%2Finicio
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] Las rutas nuevas son privadas por defecto; las públicas están declaradas solo en `PUBLIC_ROUTES`.
- [ ] Ningún componente de cliente importa el DAL; los datos de usuario llegan como *props* con el DTO mínimo.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Coste de `GET /users/me`:** se llama una vez por petición (gracias a `cache` de React). Es aceptable para el MVP. Si hiciera falta, se podría validar el JWT en Next, aunque eso exigiría compartir `JWT_SECRET` con el frontend.
- **La *cookie* inválida no se borra al renderizar:** Next solo permite modificar *cookies* en *Server Actions* y *Route Handlers*. Se sobrescribe en el siguiente inicio de sesión, y caduca sola por `maxAge`.
- **Cierre de sesión:** fuera de alcance según `user-stories.md`. Es la funcionalidad más evidente que falta, y se propone como historia para la siguiente iteración.
