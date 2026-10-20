# TK-014 · Frontend: crear una comunidad y navegación de la zona privada

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/communities/`, `app/(privado)/`) |
| **Historia** | HU-04 Crear una comunidad (Épica 2) |
| **Prioridad** | Alta |
| **Depende de** | TK-009, TK-013 |
| **Referencias** | `user-stories.md` HU-04; `docs/api/paths/communities.yaml` (`post`); TK-007 y TK-009 (patrones de formularios, `apiFetch` y DAL) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La zona privada solo tiene `/inicio` y `/perfil`, sin navegación común (TK-011 la dejó para las pantallas de comunidades). HU-04 pide un formulario para crear una comunidad.

**Objetivo:** añadir la cabecera de navegación de la zona privada y la página `/comunidades/nueva`. Al crearla, el vecino llega a la página de su comunidad.

## 2. Alcance

**Incluye**
- `app/(privado)/layout.tsx` con una cabecera: «EntreVecinos» (enlace a `/inicio`), «Comunidades» (`/comunidades`), «Mi perfil» (`/perfil`). Responsive (menú en columna en móvil).
- `features/communities/`: `schemas.ts` (`communitySchema`), `actions.ts` (`createCommunity`), `components/CommunityForm.tsx`, `types.ts` (`ApiCommunity`).
- Página `/comunidades/nueva`.
- Página marcador `/comunidades/[communityId]` con el nombre de la comunidad (el listado de anuncios llega en TK-029).

**No incluye**
- Búsqueda de comunidades y solicitudes (TK-016); `/comunidades` se crea allí. Hasta entonces el enlace «Comunidades» lleva a `/comunidades/nueva` (asumido).
- Edición de comunidades.

## 3. Requisitos técnicos

### 3.1 Cabecera

- El *layout* **no** comprueba la sesión (guía de Next, TK-009 §3.4): solo pinta la navegación. Cada página sigue llamando a `requireUser()`.
- El enlace activo se marca con `aria-current="page"` (componente de cliente `NavLink` con `usePathname`).

### 3.2 Validación (`communitySchema`)

| Campo | Regla | Mensaje |
|---|---|---|
| `name` | se recorta; de 1 a 120 | «El nombre de la comunidad es obligatorio.» / «Máximo 120 caracteres.» |
| `description` | opcional; máximo 2000 | «Máximo 2000 caracteres.» |
| `city` | opcional; máximo 120 | «Máximo 120 caracteres.» |
| `postal_code` | opcional; máximo 16 | «Máximo 16 caracteres.» |

Los opcionales vacíos se envían como `null`.

### 3.3 *Server Action* `createCommunity`

1. `requireUser()` y token de sesión.
2. Valida; con errores devuelve `fieldErrors` y los valores.
3. `POST /v1/communities`.
4. `201`: `redirect("/comunidades/<id>")`.
5. `401`: sesión caducada (TK-009). `422`: errores por campo. Red o `5xx`: «No se pudo crear la comunidad. Inténtalo de nuevo.».

### 3.4 Formulario

- Campos: nombre, descripción (`<textarea>`), ciudad y código postal; `TextField` de TK-007 (añadir variante `multiline` o un `TextAreaField` con la misma accesibilidad).
- Texto de ayuda bajo el nombre: «Por ejemplo, el nombre de tu urbanización o barrio.».
- Botón «Crear comunidad» desactivado mientras se envía.

### 3.5 Pruebas

- `communitySchema`: casos válidos e inválidos.
- `createCommunity`: `201` (redirige), validación sin llamada a la API, `422`, `401`, red.
- `CommunityForm`: errores por campo y valores conservados.
- `NavLink`: `aria-current` en la ruta activa.

## 4. Criterios de aceptación

**AC1 — Creación correcta (HU-04 AC1)**
- **Given** que he iniciado sesión y estoy en `/comunidades/nueva`
- **When** introduzco el nombre (y opcionalmente descripción, ciudad y código postal) y pulso «Crear comunidad»
- **Then** se me lleva a `/comunidades/<id>`, que muestra el nombre de la comunidad

**AC2 — Nombre obligatorio (HU-04 AC2)**
- **Given** que estoy en el formulario
- **When** lo envío sin nombre (incluso sin validación del navegador)
- **Then** veo «El nombre de la comunidad es obligatorio.» y no se llama a la API

**AC3 — Navegación**
- **Given** que he iniciado sesión
- **When** abro cualquier página privada, en escritorio o en móvil
- **Then** veo la cabecera con «Comunidades» y «Mi perfil», y el enlace de la sección actual marcado con `aria-current="page"`

## 5. Plan de tareas

1. `layout.tsx` del grupo `(privado)` y `NavLink`.
2. `communitySchema`, `createCommunity` y sus pruebas.
3. `CommunityForm`, `TextAreaField` y la página `/comunidades/nueva`.
4. Página marcador `/comunidades/[communityId]` (usa `GET /v1/communities/{id}`; `404` → `notFound()`).
5. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Navegador con sesión: /comunidades/nueva → crear → /comunidades/<id> con el nombre
# Enviar sin nombre (novalidate) → error bajo el campo
# Ventana de 360 px: la cabecera no provoca scroll horizontal
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los tres criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Destino del enlace «Comunidades»:** provisional hasta TK-016.
- **Cierre de sesión:** la cabecera es el lugar natural para él, pero sigue fuera de alcance (`user-stories.md`).
