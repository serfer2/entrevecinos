# TK-018 · Frontend: gestión de solicitudes de acceso

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/communities/admin/`, `app/(privado)/comunidades/[communityId]/gestion/`) |
| **Historia** | HU-06 Aprobar o rechazar solicitudes de acceso (Épica 2) |
| **Prioridad** | Alta |
| **Depende de** | TK-016, TK-017 |
| **Referencias** | `user-stories.md` HU-06; `docs/api/paths/communities_community_id_memberships*.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-06 pide que el administrador vea las solicitudes pendientes con el nombre de cada solicitante y las apruebe o rechace, y que un miembro sin ese rol no tenga acceso a esa gestión.

**Objetivo:** crear la página `/comunidades/[communityId]/gestion/solicitudes`, visible y accesible solo para administradores, con las acciones «Aprobar» y «Rechazar».

## 2. Alcance

**Incluye**
- Enlace «Gestionar comunidad» en la página de la comunidad, solo si mi rol es `community_admin`.
- Página de solicitudes pendientes (paginada) con nombre y fecha de solicitud.
- *Server Action* `reviewRequest(communityId, userId, decision)`.
- Página «Sin permisos» común para respuestas `403` (`components/ui/Forbidden.tsx`).

**No incluye**
- Listado completo de miembros, bloqueo y expulsión (TK-041).

## 3. Requisitos técnicos

### 3.1 Acceso

- La página llama a `requireUser()` y a `GET /v1/communities/{id}/memberships?status=pending`.
- `403` → muestra `Forbidden` («No tienes permisos para gestionar esta comunidad.») con enlace a la comunidad. `404` → `notFound()`.
- El enlace «Gestionar comunidad» se muestra según mi membresía (`role = community_admin`), pero ocultarlo no es la protección: la API decide (README §2.5).

### 3.2 Página de solicitudes

- Lista con nombre del solicitante y «Solicitado el <fecha>» (`Intl.DateTimeFormat("es-ES")`).
- Sin solicitudes: «No hay solicitudes pendientes.».
- Dos botones por solicitud: «Aprobar» y «Rechazar». «Rechazar» pide confirmación con un `<dialog>` accesible: «¿Rechazar la solicitud de <nombre>? No podrá volver a solicitar el acceso.» (asumido, ver TK-015 §8).
- Componente compartido `ConfirmDialog` (`components/ui/`), que reutilizarán eliminar y retirar anuncios.

### 3.3 *Server Action* `reviewRequest`

- `requireUser()`; valida que los ids son UUID y que `decision` es `approved` o `rejected`.
- `PATCH /v1/communities/{id}/memberships/{user_id}`.
- `200`: `revalidatePath` de la página y mensaje «Solicitud aprobada.» o «Solicitud rechazada.» (`role="status"`).
- `409`: «Esta solicitud ya se había revisado.» y se recarga la lista. `403`: `Forbidden`. Red o `5xx`: error general.

### 3.4 Pruebas

- `reviewRequest`: `200` (ambas decisiones), `409`, `403`, ids inválidos.
- `ConfirmDialog`: abre, confirma y cancela; foco atrapado y devuelto al botón.
- Lista: vacía, con solicitudes y botones.

## 4. Criterios de aceptación

**AC1 — Ver solicitudes (HU-06 AC1)**
- **Given** que soy administrador de una comunidad con solicitudes pendientes
- **When** abro «Gestionar comunidad»
- **Then** veo la lista de solicitudes con el nombre de cada solicitante

**AC2 — Aprobar (HU-06 AC2)**
- **Given** una solicitud pendiente
- **When** pulso «Aprobar»
- **Then** desaparece de la lista y el solicitante ve la comunidad como «Entrar» en su búsqueda y en «Mis comunidades»

**AC3 — Rechazar (HU-06 AC3)**
- **Given** una solicitud pendiente
- **When** pulso «Rechazar» y confirmo
- **Then** desaparece de la lista de pendientes y el solicitante sigue sin acceso

**AC4 — Permiso restringido (HU-06 AC4)**
- **Given** que soy miembro sin rol de administrador
- **When** abro la página de la comunidad o escribo la URL de gestión
- **Then** no veo el enlace y la URL muestra «No tienes permisos para gestionar esta comunidad.»

## 5. Plan de tareas

1. `Forbidden` y `ConfirmDialog` con sus pruebas.
2. Enlace «Gestionar comunidad» condicionado al rol.
3. Página de solicitudes y *Server Action* `reviewRequest` con pruebas.
4. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# A (admin) y B (solicitante pendiente) en dos ventanas:
#   A → /comunidades/<id> → «Gestionar comunidad» → «Aprobar» → B ve «Entrar»
#   C (miembro aprobado) → /comunidades/<id>/gestion/solicitudes → «No tienes permisos…»
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] Las acciones funcionan con teclado y el diálogo es accesible.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Aviso al solicitante:** sin notificaciones en el MVP; el vecino ve el cambio al volver a la aplicación.
