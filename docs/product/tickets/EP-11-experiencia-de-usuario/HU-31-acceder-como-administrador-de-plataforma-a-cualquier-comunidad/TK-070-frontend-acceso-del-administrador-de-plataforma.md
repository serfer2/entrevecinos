# TK-070 · Frontend: acceso del administrador de plataforma a cualquier comunidad

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/communities/access.ts`, `components/MembershipAction.tsx`, `app/(privado)/comunidades/page.tsx`, `comunidades/[communityId]/page.tsx`, `anuncios/nuevo/page.tsx`) |
| **Historia** | HU-31 Acceder como administrador de plataforma a cualquier comunidad (Épica 11) |
| **Prioridad** | Alta |
| **Depende de** | — |
| **Referencias** | HU-31; `CommunityAccess.require_member` (API) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La API deja pasar siempre a un `platform_admin` (`require_member`, `require_role`), pero la web decide qué mostrar solo por la membresía. Un administrador sin membresía aprobada ve «Solicitar acceso» o «Solicitud pendiente» y no ve los anuncios.

**Objetivo:** que la web aplique la misma regla que la API.

## 2. Alcance

**Incluye**
- `canAccessCommunity` y `canManageCommunity` en `features/communities/access.ts`, con pruebas.
- Página de la comunidad y de publicar anuncio.
- `MembershipAction` con `isPlatformAdmin`: siempre «Entrar».

**No incluye**
- La visibilidad de sus anuncios en el listado (TK-071).
- El selector de comunidad del listado, que sigue mostrando solo las membresías aprobadas.

## 3. Requisitos técnicos

| Función | Regla |
|---|---|
| `canAccessCommunity` | Membresía `approved` o `platform_admin` |
| `canManageCommunity` | `community_admin` aprobado o `platform_admin` |

- Ocultar acciones no protege nada: la API sigue decidiendo los permisos.

## 4. Criterios de aceptación

**AC1 — Buscador (HU-31 AC1)**
- **Given** un `platform_admin`
- **When** busca comunidades
- **Then** ve «Entrar» en todas, sea cual sea su membresía

**AC2 — Comunidad (HU-31 AC2)**
- **Given** un `platform_admin` con la solicitud pendiente
- **When** entra en la comunidad
- **Then** ve los anuncios, «Publicar anuncio» y «Gestionar comunidad»

## 5. Plan de tareas

1. `access.ts` con pruebas.
2. Páginas de comunidad y de publicar.
3. `MembershipAction` y buscador.

## 6. Verificación

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
make build-frontend && $COMPOSE up -d web
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck` y `test` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Selector de comunidad:** no lista las comunidades a las que el administrador accede sin ser miembro; se mantiene así a propósito.
