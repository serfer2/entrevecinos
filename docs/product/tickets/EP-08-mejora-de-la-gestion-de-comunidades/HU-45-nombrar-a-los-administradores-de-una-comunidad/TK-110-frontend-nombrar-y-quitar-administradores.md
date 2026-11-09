# TK-110 · Frontend: nombrar y quitar administradores desde la gestión de miembros

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad (con documentación) |
| **Componente** | `apps/web/` (`features/communities/admin/`, `app/(privado)/comunidades/[communityId]/gestion/miembros/`), `docs/product/user-stories.md`, `readme.md` |
| **Historia** | HU-45 Nombrar a los administradores de una comunidad (Épica 8) |
| **Prioridad** | Alta |
| **Depende de** | TK-041, TK-070, TK-109 |
| **Referencias** | `features/communities/admin/members.ts` (`rowActions`, `MEMBER_ACTIONS`, `MEMBER_CONFLICTS`); `features/communities/admin/actions.ts` (`manageMember`); `components/ui/ConfirmDialog` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El `platform_admin` ya entra en cualquier comunidad y abre «Gestionar comunidad» → «Miembros» (TK-041, TK-070), donde ve a los miembros con su rol y su estado (HU-45 AC1). Pero no puede cambiar el rol de nadie: las filas de administradores no tienen acciones. TK-109 añade el cambio de rol a la API.

**Objetivo:** añadir a la página de miembros las acciones «Nombrar administrador» y «Quitar administrador», visibles solo para el `platform_admin`.

## 2. Alcance

**Incluye**
- Acciones nuevas por fila, con confirmación y mensaje de resultado.
- Mensajes de los `409` de TK-109.
- Documentación del rol en `user-stories.md` y `readme.md`.

**No incluye**
- El rol «Moderador».
- Una página de administración con todas las comunidades: el `platform_admin` llega a cada comunidad desde la búsqueda («Entrar», HU-31).
- Cambios para `community_admin` o miembros: ven la página exactamente igual que antes.

## 3. Requisitos técnicos

### 3.1 Acciones por fila

`rowActions` recibe si el usuario actual es `platform_admin` (desde `requireUser()`, `user.platform_role`) y, solo en ese caso, añade:

| Fila | Acciones nuevas (`platform_admin`) |
|---|---|
| miembro aprobado (no administrador) | «Nombrar administrador» (además de «Bloquear» y «Expulsar») |
| administrador aprobado (incluido uno mismo, si es miembro) | «Quitar administrador» |
| pendiente, rechazado o bloqueado | ninguna nueva |

Para el resto de usuarios, la tabla de TK-041 no cambia. La API decide igualmente (TK-109): ocultar el botón no protege nada.

### 3.2 *Server Action*

- `MEMBER_ACTIONS` gana `nombrar-admin` y `quitar-admin`, con `{ role: "community_admin" | "member", done: "nombrado administrador" | "ya no es administrador" }`.
- `manageMember` envía `PATCH` con `{ role }` para esas acciones y `{ status }` para las demás. Sigue llamando a `requireUser()`, valida los identificadores y hace `revalidatePath`.
- Mensajes (`role="status"`): «<nombre> ha sido nombrado administrador.» y «<nombre> ya no es administrador.».
- `409` → `conflictCode`: añade el código `solo-aprobados` («Solo se puede cambiar el rol de un miembro aprobado.»). `ultimo-admin` ya existe. `403` → `Forbidden`.

### 3.3 Confirmaciones (`ConfirmDialog`)

- Nombrar: «¿Nombrar a <nombre> administrador de <comunidad>? Podrá aprobar solicitudes, gestionar miembros y ocultar anuncios, y recibirá los avisos de nuevas solicitudes.»
- Quitar: «¿Quitar a <nombre> el rol de administrador? Seguirá siendo miembro, pero dejará de gestionar la comunidad.»

### 3.4 Documentación

- `docs/product/user-stories.md`, «Roles»: el administrador de comunidad es quien la crea o a quien nombra el administrador de plataforma (HU-45).
- `readme.md` §1.2 «Comunidades y zonas» / MVP «Administración mínima»: una línea con el nombramiento de administradores por la plataforma.

### 3.5 Pruebas

- `members.test.ts`: tabla de §3.1 con y sin `platform_admin` (incluidas las filas de uno mismo y del administrador), y `conflictCode` con el nuevo detalle.
- `actions.test.ts`: `nombrar-admin` y `quitar-admin` envían `{ role }`; éxito, `409` (último administrador, solo aprobados) y `403`.

## 4. Criterios de aceptación

**AC1 — Ver miembros y rol (HU-45 AC1)**
- **Given** que soy `platform_admin`
- **When** entro en una comunidad → «Gestionar comunidad» → «Miembros»
- **Then** veo cada miembro con su rol y su estado

**AC2 — Nombrar (HU-45 AC2)**
- **Given** un miembro aprobado
- **When** pulso «Nombrar administrador» y confirmo
- **Then** veo «<nombre> ha sido nombrado administrador.», su rol pasa a «Administrador» y, en su sesión, ve «Gestionar comunidad»

**AC3 — Quitar (HU-45 AC3 y AC4)**
- **Given** una comunidad con dos administradores
- **When** quito el rol a uno y confirmo
- **Then** veo «<nombre> ya no es administrador.»; si después intento quitárselo al último, veo «La comunidad debe tener al menos un administrador.»

**AC4 — Sin acciones para otros roles (HU-45 AC6)**
- **Given** que soy `community_admin`
- **When** abro «Miembros»
- **Then** no veo «Nombrar administrador» ni «Quitar administrador»

## 5. Plan de tareas

1. `rowActions` y `MEMBER_ACTIONS` con los roles.
2. `manageMember` y mensajes de conflicto.
3. Botones y confirmaciones en la página.
4. Pruebas.
5. Documentación (§3.4) y verificación (§6).

## 6. Verificación

```bash
make dev
# platform_admin: buscar una comunidad → Entrar → Gestionar comunidad → Miembros
# «Nombrar administrador» a B → B (otra ventana) ve «Gestionar comunidad» y la pestaña Solicitudes
# «Quitar administrador» a B → B recibe «No tienes permisos para gestionar esta comunidad.»
# Quitar el rol al único administrador → mensaje de último administrador
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] Las acciones son usables en móvil y con teclado.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [x] `user-stories.md` y `readme.md` actualizados.
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Encontrar la comunidad:** el `platform_admin` llega a cada comunidad por la búsqueda. Si hay muchas, una lista de todas las comunidades activas en `/admin/comunidades` (hoy solo muestra las pendientes) sería otra historia.
