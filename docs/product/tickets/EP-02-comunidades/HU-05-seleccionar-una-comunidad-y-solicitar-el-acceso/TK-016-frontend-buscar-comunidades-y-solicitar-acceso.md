# TK-016 · Frontend: buscar comunidades, solicitar el acceso y mis comunidades

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/communities/`, `app/(privado)/comunidades/`, `/inicio`) |
| **Historia** | HU-05 Seleccionar una comunidad y solicitar el acceso (Épica 2) |
| **Prioridad** | Alta |
| **Depende de** | TK-014, TK-015 |
| **Referencias** | `user-stories.md` HU-05; `docs/api/paths/communities.yaml` (`get`), `communities_community_id_memberships.yaml` (`post`), `users_me_memberships.yaml` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-05 pide encontrar la comunidad, solicitar el acceso, ver que la solicitud está pendiente y no poder ver sus anuncios hasta la aprobación. El vecino también necesita un punto de entrada a sus comunidades.

**Objetivo:** crear la página de búsqueda `/comunidades`, el botón «Solicitar acceso» con el estado de cada comunidad, la sección «Mis comunidades» en `/inicio` y el aviso de solicitud pendiente en la página de una comunidad.

## 2. Alcance

**Incluye**
- `/comunidades`: formulario de búsqueda (`q`, ciudad, código postal) por GET, resultados paginados y enlace «Crear una comunidad» (`/comunidades/nueva`).
- Componente compartido `Pagination` (`components/ui/`), reutilizable por los listados de anuncios.
- Botón «Solicitar acceso» por resultado, con el estado actual si ya hay membresía.
- `/inicio`: «Mis comunidades» con su estado; sin comunidades, invitación a buscar o crear una.
- `/comunidades/[communityId]`: si la membresía no está aprobada, aviso del estado en lugar del contenido (HU-05 AC3).
- El enlace «Comunidades» de la cabecera apunta ya a `/comunidades`.

**No incluye**
- Listado de anuncios de la comunidad (TK-029).

## 3. Requisitos técnicos

### 3.1 Búsqueda (`/comunidades`)

- Server Component que lee `searchParams` (`q`, `city`, `postal_code`, `page`), los valida (longitudes del contrato; valores inválidos se ignoran) y llama a `GET /v1/communities`.
- El formulario usa `method="get"` y conserva los valores; cambiar un filtro vuelve a la página 1.
- Cada resultado muestra nombre, ciudad y código postal, y la acción según mi membresía (obtenida con `GET /v1/users/me/memberships`, una vez por petición):

| Mi estado | Se muestra |
|---|---|
| sin membresía | botón «Solicitar acceso» |
| `pending` | «Solicitud pendiente» |
| `approved` | enlace «Entrar» a `/comunidades/<id>` |
| `rejected` / `blocked` | «Acceso no disponible» (asumido) |

- Sin resultados: «No hemos encontrado comunidades con esos datos.» y enlace para crear una.

### 3.2 *Server Action* `requestAccess(communityId)`

- `requireUser()`, `POST /v1/communities/{id}/memberships`.
- `201` o `409`: `revalidatePath("/comunidades")` e `/inicio`; el estado se pinta a partir de las membresías (HU-05 AC4: con `409` se muestra el estado actual, no un error).
- `404`: «Esta comunidad ya no está disponible.». Red o `5xx`: error general.
- El formulario de cada resultado envía el id en un campo oculto; la acción valida que sea un UUID.

### 3.3 `Pagination`

- Recibe `page`, `pageSize`, `total` y una función para construir el `href`; enlaces «Anterior» y «Siguiente» y el texto «Página X de Y». `<nav aria-label="Paginación">`. Sin enlaces cuando no aplican.

### 3.4 Página de una comunidad sin acceso

- `/comunidades/[communityId]` obtiene la comunidad y mi membresía. Si no está `approved`, muestra el nombre y el aviso:
  - `pending`: «Tu solicitud está pendiente de aprobación. Podrás ver y publicar anuncios cuando un administrador la apruebe.»
  - sin membresía: botón «Solicitar acceso».
  - `rejected` / `blocked`: «No tienes acceso a esta comunidad.»

### 3.5 Pruebas

- Validación de `searchParams` y construcción de URLs de paginación.
- `requestAccess`: `201`, `409`, `404`, red.
- Componente de resultado: acción correcta para cada estado.
- `Pagination`: enlaces y textos en primera, intermedia y última página.

## 4. Criterios de aceptación

**AC1 — Búsqueda (HU-05 AC1)**
- **Given** que he iniciado sesión
- **When** busco por nombre, ciudad o código postal en `/comunidades`
- **Then** veo las comunidades que coinciden, paginadas, con la acción que corresponde a mi estado

**AC2 — Solicitud (HU-05 AC2)**
- **Given** una comunidad de la que no soy miembro
- **When** pulso «Solicitar acceso»
- **Then** el resultado pasa a «Solicitud pendiente» y la comunidad aparece en «Mis comunidades» de `/inicio` como pendiente

**AC3 — Sin acceso hasta la aprobación (HU-05 AC3)**
- **Given** que mi solicitud está pendiente
- **When** abro `/comunidades/<id>`
- **Then** veo el aviso de solicitud pendiente y ningún anuncio ni opción de publicar

**AC4 — Solicitud duplicada (HU-05 AC4)**
- **Given** que ya tengo una membresía (por ejemplo, abriendo la búsqueda en dos pestañas)
- **When** vuelvo a pulsar «Solicitar acceso»
- **Then** no se crea otra solicitud y veo mi estado actual, sin mensaje de error

## 5. Plan de tareas

1. `Pagination` y sus pruebas.
2. Página `/comunidades` (búsqueda, resultados, estado) y cabecera.
3. *Server Action* `requestAccess` y sus pruebas.
4. «Mis comunidades» en `/inicio`.
5. Aviso de acceso en `/comunidades/[communityId]`.
6. Verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Usuario A crea «Urbanización Los Olivos»; usuario B (otra ventana):
#   /comunidades?q=olivos → resultado con «Solicitar acceso» → «Solicitud pendiente»
#   /inicio → «Mis comunidades» con la comunidad pendiente
#   /comunidades/<id> → aviso de solicitud pendiente
#   abrir la búsqueda en otra pestaña antigua y pulsar «Solicitar acceso» → estado pendiente, sin error
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cuatro criterios de aceptación se cumplen.
- [ ] La búsqueda funciona sin JavaScript (formulario GET).
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Texto para `rejected` / `blocked`:** neutro a propósito, para no señalar al vecino.
- **Notificar al administrador de nuevas solicitudes:** las notificaciones son post-MVP; el administrador las verá al abrir la gestión (TK-018).
