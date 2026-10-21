# TK-048 · Frontend: llevar a la lista de comunidades tras el registro o el inicio de sesión si no pertenezco a ninguna

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (*Server Actions* `signup` y `login`, `features/auth`) |
| **Historia** | HU-19 Buscar comunidades al registrarme o iniciar sesión si no pertenezco a ninguna (Épica 7) |
| **Prioridad** | Alta |
| **Depende de** | TK-007, TK-009, TK-016 |
| **Referencias** | `user-stories.md` HU-19 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Tras registrarse, `signup` redirige siempre a `/inicio`; tras iniciar sesión, `login` redirige a `next` o a `/inicio`. Un vecino sin comunidades ve en `/inicio` «Todavía no perteneces a ninguna comunidad» y tiene que pulsar un enlace más para llegar a `/comunidades`.

**Objetivo:** que el vecino recién registrado y, sin `next`, el que inicia sesión sin ser miembro aprobado de ninguna comunidad lleguen directamente a `/comunidades`.

## 2. Alcance

**Incluye**
- Función `postLoginPath(token)` que calcula el destino a partir de las membresías del usuario.
- Usarla en la *Server Action* `login` cuando no hay un `next` seguro.
- Redirigir a `/comunidades` al terminar el registro (`signup`).

**No incluye**
- El destino con una sola comunidad (TK-049).
- Cambios en la API: `GET /v1/users/me/memberships` (TK-015) ya devuelve las membresías del usuario en cualquier estado.

## 3. Requisitos técnicos

### 3.1 Destino tras el inicio de sesión

- `postLoginPath(token: string): Promise<string>` en `features/auth/` (servidor). Llama a `GET /v1/users/me/memberships?status=approved` con `apiFetch` y el token recién emitido, sin depender de la *cookie* que se acaba de escribir.
- Solo cuentan las membresías `approved` (asumido). Con `pending`, `rejected` o `blocked` el usuario no ve anuncios de esa comunidad, así que se trata como sin comunidades; en `/comunidades` verá el estado de su solicitud.
- Se descartan las membresías cuya comunidad tiene `is_active: false`: la API las devuelve si están aprobadas, pero su página responde 404.
- Ninguna aprobada → `/comunidades`. En otro caso → `HOME_PATH`.
- Si la llamada falla (red, `5xx`), → `HOME_PATH` (asumido): el inicio de sesión ya se ha completado y no debe fallar por esto.
- La ruta `/comunidades` se define como constante junto a las demás de `routes.ts` (`COMMUNITIES_PATH`).

### 3.2 *Server Action* `login`

- `redirect(safeNextPath(formData.get("next")) ?? (await postLoginPath(token)))`: un `next` seguro tiene prioridad (asumido; mantiene el requisito «Inicio de sesión desde el navegador» de `web-session`).
- La consulta de membresías solo se hace cuando no hay `next`.

### 3.3 *Server Action* `signup`

- Tras `createSession`, `redirect(COMMUNITIES_PATH)` en lugar de `HOME_PATH`. Sin consultar las membresías: una cuenta recién creada no tiene ninguna.
- Cambia el requisito «Registro desde el navegador» de `web-signup` (hoy redirige a `/inicio`); se actualiza al archivar el cambio de OpenSpec.

### 3.4 Pruebas

- `signup`: con `201` crea la sesión y redirige a `/comunidades` (sustituye la prueba que espera `/inicio`).
- `postLoginPath`: sin membresías aprobadas, solo aprobada en una comunidad desactivada, alguna `approved`, error de la API; la petición lleva `status=approved`.
- `login`: sin `next` y sin comunidades → `/comunidades`; con `next` → `next`, sin consultar las membresías.

## 4. Criterios de aceptación

**AC1 — Sin comunidades (HU-19 AC1)**
- **Given** un usuario sin membresías aprobadas
- **When** inicia sesión desde `/iniciar-sesion`
- **Then** queda en `/comunidades`

**AC2 — Registro (HU-19 AC2)**
- **Given** que no tengo cuenta
- **When** completo el registro en `/registro`
- **Then** quedo en `/comunidades` con la sesión iniciada

**AC3 — Solicitud pendiente (HU-19 AC1)**
- **Given** un usuario cuya única membresía está `pending`
- **When** inicia sesión
- **Then** queda en `/comunidades` y ve su solicitud como pendiente

**AC4 — Destino solicitado (HU-19 AC3)**
- **Given** un usuario sin comunidades que abre `/perfil` sin sesión
- **When** inicia sesión desde `/iniciar-sesion?next=%2Fperfil`
- **Then** queda en `/perfil`

**AC5 — API de membresías caída**
- **Given** que `GET /v1/users/me/memberships` responde `5xx`
- **When** el usuario inicia sesión
- **Then** queda en `/inicio` con la sesión iniciada

## 5. Plan de tareas

1. `COMMUNITIES_PATH` y `postLoginPath` con pruebas.
2. Usarla en `login` y ampliar sus pruebas.
3. Redirección de `signup` a `/comunidades` y su prueba.
4. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# /registro → crear cuenta → /comunidades
# Borrar la cookie ev_session → iniciar sesión con esa cuenta → /comunidades
# Solicitar acceso a una comunidad → iniciar sesión de nuevo → /comunidades con «Solicitud pendiente»
# Sin sesión, abrir /perfil → iniciar sesión → /perfil
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Solicitudes pendientes:** si se prefiere que un usuario con una solicitud pendiente llegue a `/inicio`, basta con contar también `pending` en §3.1.
- **Una llamada más al iniciar sesión:** añade una petición a la API solo cuando no hay `next`.
