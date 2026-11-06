# TK-071 · Backend: anuncios del administrador de plataforma visibles en el listado

| Campo | Valor |
|---|---|
| **Tipo** | Backend / funcionalidad |
| **Componente** | `apps/api/` (`infrastructure/listings/sqlalchemy_listing_repository.py`), `openspec/specs/community-authorization/spec.md` |
| **Historia** | HU-31 Acceder como administrador de plataforma a cualquier comunidad (Épica 11) |
| **Prioridad** | Alta |
| **Depende de** | TK-070 |
| **Referencias** | HU-31 AC3; TK-040 (anuncios de miembros bloqueados o expulsados) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El listado solo muestra anuncios cuyo autor tiene una membresía aprobada (`OWNER_IS_MEMBER`, TK-040). Tras TK-070, un `platform_admin` puede publicar sin membresía aprobada y su anuncio no aparece en el listado, ni siquiera para él.

**Objetivo:** que un autor `platform_admin` cuente como miembro aprobado, igual que en `require_member`.

## 2. Alcance

**Incluye**
- `OWNER_IS_MEMBER`: membresía aprobada **o** autor `platform_admin`.
- Prueba de integración.
- Especificación `community-authorization`.

**No incluye**
- Cambios de contrato: el esquema de respuesta no cambia.

## 3. Requisitos técnicos

- `EXISTS` sobre un alias propio de `users`: la consulta exterior ya une `users` y el subselect no debe correlacionarse con ella.
- Afecta al listado, la búsqueda, el `total` y el detalle (`owner_is_member`).
- Los anuncios de vecinos bloqueados o expulsados siguen ocultos.

## 4. Criterios de aceptación

**AC1 — Anuncio del administrador (HU-31 AC3)**
- **Given** un `platform_admin` con la solicitud pendiente que publica en una comunidad
- **When** otro miembro abre el listado y el detalle
- **Then** ve el anuncio

**AC2 — Bloqueados (TK-040)**
- **Given** un miembro bloqueado con anuncios
- **When** otro miembro abre el listado
- **Then** no los ve, como hasta ahora

## 5. Plan de tareas

1. Regla en el repositorio.
2. Prueba en `test_members_management.py`.
3. Especificación.

## 6. Verificación

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE run --rm -v "$PWD/apps/api/tests:/app/tests" api python -m pytest -q
$COMPOSE run --rm api ruff check src
```

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck` y `test` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Administrador bloqueado en una comunidad:** sus anuncios se siguen mostrando, coherente con que `require_member` le deja pasar siempre.
