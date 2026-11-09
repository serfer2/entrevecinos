# TK-113 · Frontend: rechazar desde «Comunidades pendientes»

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/platform-admin/`, `app/(privado)/admin/comunidades/`) |
| **Historia** | HU-47 Rechazar una comunidad pendiente (Épica 8) |
| **Prioridad** | Media |
| **Depende de** | TK-051, TK-112 |
| **Referencias** | `features/platform-admin/actions.ts` (`approveCommunity`); `features/platform-admin/paths.ts` (`PENDING_COMMUNITIES_RESULT_MESSAGES`); `components/ui/ConfirmDialog` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

«Comunidades pendientes» (`/admin/comunidades`, TK-051) solo tiene el botón «Aprobar». TK-112 añade el rechazo a la API, y el correo de TK-111 enlaza a esta página para aprobar o rechazar.

**Objetivo:** añadir «Rechazar», con confirmación, a cada comunidad pendiente, y un ancla por comunidad para el enlace del correo.

## 2. Alcance

**Incluye**
- Botón «Rechazar» con `ConfirmDialog` en cada fila.
- *Server Action* `rejectCommunity` y sus mensajes de resultado.
- Ancla `id="comunidad-<id>"` en cada fila.

**No incluye**
- Motivo del rechazo ni aviso al creador (ver TK-112 §8).

## 3. Requisitos técnicos

### 3.1 Página

- Junto a «Aprobar», un `ConfirmDialog`:
  - botón y confirmación: «Rechazar»;
  - título: «¿Rechazar la comunidad <nombre>?»;
  - mensaje: «Se eliminará y desaparecerá de las comunidades de quien la creó, que podrá crear otra. No se puede deshacer.»
- Cada `<li>` lleva `id="comunidad-<id>"` y `scroll-margin-top`, para que el enlace del correo (TK-111) lleve a la comunidad aunque haya varias pendientes.

### 3.2 *Server Action* `rejectCommunity`

- En `features/platform-admin/actions.ts`: `requireUser()`, `community_id` validado con `isUuid`, `DELETE /admin/communities/{id}` con `userApiFetch`, `revalidatePath(PENDING_COMMUNITIES_PATH)` y `revalidatePath("/inicio")`.
- El nombre de la comunidad viaja en un campo oculto, acotado a 120 caracteres como en `manageMember`, para el mensaje de resultado.
- Resultado en la URL, con códigos fijos y el nombre:
  - `204` → `?resultado=rechazada&nombre=<nombre>` → «Se ha rechazado la comunidad <nombre>.»;
  - `409` → `?resultado=ya-activa` → «Esta comunidad ya está activa: no se puede rechazar.»;
  - `404` → `?resultado=no-existe` → «Esta comunidad ya no está pendiente.»;
  - cualquier otro → `?resultado=error-rechazo` → «No se pudo rechazar la comunidad. Inténtalo de nuevo.».
- `PENDING_COMMUNITIES_RESULT_MESSAGES` admite mensajes con el nombre (función o plantilla) sin romper los de «Aprobar».

### 3.3 Documentación

- `apps/web/README.md`, «Gestión de comunidades y administración»: en la fila de `/admin/comunidades`, añadir «Rechazar» (`rejectCommunity`, con confirmación) y el ancla `#comunidad-<id>` que usa el correo de TK-111.

### 3.4 Pruebas

- `actions.test.ts`: `DELETE` con el id; redirección por cada resultado (`204`, `409`, `404`, error); id no válido sin llamar a la API.
- Página o mensajes: el mensaje con el nombre, y `role="status"` frente a `role="alert"` en los errores.

## 4. Criterios de aceptación

**AC1 — Rechazar (HU-47 AC1)**
- **Given** que soy `platform_admin` y hay una comunidad pendiente
- **When** pulso «Rechazar» y confirmo
- **Then** veo «Se ha rechazado la comunidad <nombre>.» y deja de aparecer en la lista

**AC2 — El creador puede crear otra (HU-47 AC2)**
- **Given** la comunidad rechazada
- **When** su creador abre «Inicio» o crea una comunidad
- **Then** la rechazada no aparece y puede crear otra sin el aviso de comunidad pendiente

**AC3 — Ya aprobada (HU-47 AC3)**
- **Given** que otro administrador acaba de aprobar la comunidad
- **When** la rechazo desde una página sin actualizar
- **Then** veo «Esta comunidad ya está activa: no se puede rechazar.» y sigue activa

**AC4 — Enlace del correo**
- **Given** el enlace `/admin/comunidades#comunidad-<id>`
- **When** lo abro
- **Then** la página se desplaza a esa comunidad

## 5. Plan de tareas

1. *Server Action* y mensajes.
2. Botón, confirmación y ancla en la página.
3. Pruebas.
4. Documentación (§3.3).
5. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# platform_admin → /admin/comunidades → «Rechazar» → confirmar → mensaje y la comunidad desaparece
# Con el creador: «Inicio» ya no la muestra y puede crear otra comunidad
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [x] Los criterios de aceptación se cumplen.
- [x] El botón y el diálogo son usables en móvil y con teclado.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [x] `apps/web/README.md` actualizado (§3.3).
- [ ] Cambios revisados y fusionados mediante *pull request*.

## 8. Riesgos y decisiones abiertas

- **Acción irreversible:** la confirmación lo dice explícitamente («No se puede deshacer.»).
