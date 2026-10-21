# TK-052 · Backend: comunidades activas al momento cuando las crea un `platform_admin`

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (área `communities`), `docs/api/` |
| **Historia** | HU-22 Activar al momento las comunidades que crea un administrador de plataforma (Épica 8) |
| **Prioridad** | Media |
| **Depende de** | TK-050 |
| **Referencias** | `docs/api/paths/communities.yaml` (`post`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Con TK-050, toda comunidad nueva queda pendiente, también las que crea un `platform_admin`, que tendría que aprobar las suyas.

**Objetivo:** que `POST /communities` cree la comunidad activa cuando el creador es `platform_admin`.

## 2. Alcance

**Incluye**
- `CreateCommunity` decide `is_active` según el rol de plataforma del creador.
- Descripción de `createCommunity` en el contrato.

**No incluye**
- Cambios en la web: tras crear, `createCommunity` ya redirige a `/comunidades/{id}` cuando la respuesta trae `is_active: true` (TK-051 §3.1).

## 3. Requisitos técnicos

### 3.1 Creación

- `CreateCommunity.execute(community, creator: User)`: `is_active = creator.platform_role is PlatformRole.PLATFORM_ADMIN`. El endpoint ya dispone del usuario autenticado.
- El creador sigue quedando como `community_admin` aprobado, también el `platform_admin` (asumido: así aparece en «Mis comunidades» y gestiona la comunidad como cualquier administrador).

### 3.2 Contrato

- `communities.yaml` (`post`): las comunidades que crea un `platform_admin` se crean con `is_active: true`.
- `docs/api/README.md`: fila TK-052 en «Cambios».

### 3.3 Pruebas

- Caso de uso: vecino → pendiente; `platform_admin` → activa.
- API: un `platform_admin` crea una comunidad que responde `is_active: true`, aparece en la búsqueda y se puede abrir.

## 4. Criterios de aceptación

**AC1 — Comunidad activa (HU-22 AC1)**
- **Given** un `platform_admin`
- **When** hace `POST /v1/communities`
- **Then** recibe `201` con `is_active: true`, la comunidad aparece en `GET /v1/communities` y es su `community_admin`

**AC2 — Vecinos (HU-22 AC2)**
- **Given** un usuario sin rol `platform_admin`
- **When** hace `POST /v1/communities`
- **Then** recibe `201` con `is_active: false`

## 5. Plan de tareas

1. `CreateCommunity` con el usuario creador y su rol.
2. Contrato y `docs/api/README.md`.
3. Pruebas y verificación según la sección 6.

## 6. Verificación

```bash
make dev
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
# platform_admin: /comunidades/nueva → crear → /comunidades/<id> con la comunidad activa
```

## 7. Definición de terminado

- [ ] Los dos criterios de aceptación se cumplen.
- [ ] Las pruebas de la API y el lint pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- Ninguno relevante.
