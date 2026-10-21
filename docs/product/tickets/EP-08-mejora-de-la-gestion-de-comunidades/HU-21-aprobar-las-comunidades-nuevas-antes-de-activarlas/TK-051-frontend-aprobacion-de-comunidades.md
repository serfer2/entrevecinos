# TK-051 · Frontend: comunidades pendientes y página de aprobación

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (crear comunidad, `/inicio`, `/admin/comunidades`) |
| **Historia** | HU-21 Aprobar las comunidades nuevas antes de activarlas (Épica 8) |
| **Prioridad** | Alta |
| **Depende de** | TK-014, TK-016, TK-050 |
| **Referencias** | `user-stories.md` HU-21 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Con TK-050, una comunidad recién creada queda inactiva y su página responde `404`. Hoy, tras crearla, la web redirige a esa página, y en «Mis comunidades» se enlaza aunque no se pueda abrir.

**Objetivo:** explicar al creador que su comunidad está pendiente y dar al `platform_admin` una página para aprobarlas.

## 2. Alcance

**Incluye**
- Destino tras crear una comunidad según `is_active`.
- Comunidades pendientes en «Mis comunidades» de `/inicio`.
- Página `/admin/comunidades` con las pendientes y el botón «Aprobar».

**No incluye**
- Rechazar comunidades (ver TK-050 §2).
- Un menú de administración en la cabecera: el acceso se ofrece desde `/inicio` (asumido).

## 3. Requisitos técnicos

### 3.1 Crear una comunidad

- `createCommunity`: con `is_active: true` → `/comunidades/{id}` (como ahora; es el caso del `platform_admin`, TK-052); con `false` → `/inicio?comunidad-pendiente=1`.
- `/inicio` con ese parámetro: aviso `role="status"` «Hemos recibido tu comunidad. Un administrador la revisará antes de activarla.».
- `/comunidades/nueva`: el texto de ayuda avisa de la revisión: «Un administrador la revisará antes de activarla. Después serás su administrador y podrás aprobar a los vecinos que pidan unirse.».

### 3.2 «Mis comunidades»

- Una comunidad con `is_active: false` se muestra sin enlace y con la etiqueta «Pendiente de aprobación» en lugar del estado de la membresía.
- `postLoginPath` ya ignora las comunidades inactivas (TK-048).

### 3.3 `/admin/comunidades`

- `requireUser()`; sin `platform_role === "platform_admin"` → `notFound()` (no revela la página).
- `GET /v1/admin/communities?is_active=false&page=N`; lista con nombre, ubicación, descripción y fecha de creación; paginación con `Pagination`.
- Sin pendientes: «No hay comunidades pendientes de aprobación.».
- «Aprobar» envía la *Server Action* `approveCommunity(formData)` (`features/platform-admin/`): `PATCH /v1/admin/communities/{id}` con `{"is_active": true}`, `revalidatePath` de la página y de `/inicio`, y redirección a `/admin/comunidades?resultado=aprobada` con «Comunidad aprobada.». Error o identificador no válido → `?resultado=error` con «No se pudo aprobar la comunidad. Inténtalo de nuevo.» (mismo patrón que la revisión de solicitudes, TK-018).
- En `/inicio`, solo para el `platform_admin`, enlace «Comunidades pendientes de aprobación».

### 3.4 Pruebas

- `createCommunity`: destino con `is_active` verdadero y falso.
- `approveCommunity`: éxito, error, identificador no válido.

## 4. Criterios de aceptación

**AC1 — Comunidad pendiente (HU-21 AC1)**
- **Given** un vecino con sesión
- **When** crea una comunidad
- **Then** llega a `/inicio` con el aviso de revisión y ve la comunidad en «Mis comunidades» como «Pendiente de aprobación», sin enlace

**AC2 — Revisión (HU-21 AC2)**
- **Given** un `platform_admin`
- **When** pulsa «Comunidades pendientes de aprobación» en `/inicio`
- **Then** ve las comunidades pendientes, la más antigua primero

**AC3 — Aprobación (HU-21 AC3)**
- **Given** un `platform_admin` en `/admin/comunidades`
- **When** pulsa «Aprobar» en una comunidad
- **Then** ve «Comunidad aprobada.», la comunidad desaparece de la lista y su creador puede entrar en ella

**AC4 — Restricción (HU-21 AC4)**
- **Given** un vecino sin rol `platform_admin`
- **When** abre `/admin/comunidades`
- **Then** ve la página de no encontrado, y en `/inicio` no tiene el enlace

## 5. Plan de tareas

1. Destino de `createCommunity`, aviso en `/inicio` y texto de `/comunidades/nueva`.
2. Comunidades pendientes en «Mis comunidades».
3. Página `/admin/comunidades`, *Server Action* `approveCommunity` y enlace en `/inicio`.
4. Pruebas y verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Vecino: /comunidades/nueva → crear → /inicio con el aviso y «Pendiente de aprobación»
# platform_admin (UPDATE users SET platform_role = 'platform_admin' ...): /inicio → enlace → Aprobar
# Vecino: /inicio → la comunidad ya enlaza y se puede abrir; /admin/comunidades → no encontrado
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Aviso al creador:** no hay notificaciones; el creador descubre la aprobación al volver a `/inicio`.
