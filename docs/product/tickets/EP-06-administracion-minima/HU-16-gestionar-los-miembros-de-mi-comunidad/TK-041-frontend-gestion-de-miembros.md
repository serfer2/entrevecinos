# TK-041 · Frontend: gestión de miembros (listado, bloqueo y expulsión)

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/communities/admin/`, `app/(privado)/comunidades/[communityId]/gestion/miembros/`) |
| **Historia** | HU-16 Gestionar los miembros de mi comunidad (Épica 6) |
| **Prioridad** | Media |
| **Depende de** | TK-018, TK-040 |
| **Referencias** | `user-stories.md` HU-16 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-16 pide que el administrador vea los miembros con su estado y pueda expulsarlos o bloquearlos, y que un miembro sin rol no tenga acceso a esta función. TK-018 creó la gestión de solicitudes.

**Objetivo:** añadir la página «Miembros» a la gestión de la comunidad, con pestañas «Solicitudes» y «Miembros», y las acciones de bloquear, desbloquear y expulsar.

## 2. Alcance

**Incluye**
- Navegación de la gestión: «Solicitudes» (TK-018) y «Miembros».
- Página de miembros paginada, con filtro por estado.
- Acciones con confirmación: «Bloquear», «Desbloquear», «Expulsar».

**No incluye**
- Cambio de roles y salida voluntaria (sin historia).

## 3. Requisitos técnicos

### 3.1 Página `/comunidades/[communityId]/gestion/miembros`

- Mismo control de acceso que TK-018 (`403` → `Forbidden`).
- Tabla (en móvil, lista) con nombre, rol («Administrador», «Miembro»), estado («Pendiente», «Miembro», «Bloqueado», «Rechazado») y «Miembro desde <fecha>».
- Filtro por estado (`?estado=`), con «Todos» por defecto; paginación (`Pagination`).
- Acciones por fila, según estado y rol:

| Fila | Acciones |
|---|---|
| miembro aprobado (no administrador) | «Bloquear», «Expulsar» |
| bloqueado | «Desbloquear», «Expulsar» |
| pendiente | «Ir a solicitudes» |
| administrador o yo mismo | ninguna |

### 3.2 Confirmaciones (`ConfirmDialog`)

- Bloquear: «¿Bloquear a <nombre>? Dejará de ver y publicar anuncios, sus anuncios dejarán de mostrarse en la comunidad y no podrá volver a solicitar el acceso.»
- Expulsar: «¿Expulsar a <nombre>? Dejará de ver y publicar anuncios y sus anuncios dejarán de mostrarse, aunque podrá volver a solicitar el acceso.»
- Desbloquear: sin confirmación.

### 3.3 *Server Actions*

- `blockMember`, `unblockMember` (`PATCH` con `status`) y `removeMember` (`DELETE`): `requireUser()`, ids validados, `revalidatePath`.
- Mensajes: «<nombre> ha sido bloqueado.», «… desbloqueado.», «… expulsado.» (`role="status"`).
- `409` → mensaje de la API (último administrador, no se puede bloquear a un administrador). `403` → `Forbidden`.

### 3.4 Pruebas

- Acciones disponibles por fila (tabla de §3.1).
- *Server Actions*: éxito, `409`, `403`.
- Navegación de la gestión con `aria-current`.

## 4. Criterios de aceptación

**AC1 — Listado de miembros (HU-16 AC1)**
- **Given** que soy administrador
- **When** abro «Gestionar comunidad» → «Miembros»
- **Then** veo la lista de miembros con su rol y su estado, y puedo filtrar por estado

**AC2 — Expulsar o bloquear (HU-16 AC2)**
- **Given** un miembro que incumple las normas
- **When** lo bloqueo o lo expulso y confirmo
- **Then** veo el mensaje de confirmación, ese vecino deja de ver los anuncios de la comunidad en su sesión y sus anuncios dejan de aparecer en el listado

**AC3 — Restricción a administradores (HU-16 AC3)**
- **Given** que soy miembro sin rol de administrador
- **When** escribo la URL de gestión de miembros
- **Then** veo «No tienes permisos para gestionar esta comunidad.»

## 5. Plan de tareas

1. Navegación de la gestión (pestañas).
2. Página de miembros con filtro y paginación.
3. *Server Actions* y confirmaciones, con pruebas.
4. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Admin: Gestionar comunidad → Miembros → «Bloquear» a B → B (otra ventana) ve «No tienes acceso a esta comunidad.»
# «Desbloquear» → B vuelve a ver los anuncios; «Expulsar» a C → C puede volver a solicitar
# Miembro sin rol → URL de gestión → sin permisos
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] La tabla es usable en móvil y con teclado.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Motivo del bloqueo:** no se registra en el MVP; un campo de motivo ayudaría a la auditoría.
