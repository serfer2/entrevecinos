# TK-072 · Frontend: «Ocultar anuncio» en lugar de «Retirar anuncio»

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / textos |
| **Componente** | `apps/web/` (`ListingActions.tsx`, `comunidades/[communityId]/page.tsx`, `anuncios/[listingId]/not-found.tsx`, `features/listings/actions.ts`, `form.ts`), `apps/api/` (`domain/listings/errors.py`), `openspec/specs/web-community-admin/spec.md` |
| **Historia** | HU-32 Entender qué hace la moderación de un anuncio (Épica 11) |
| **Prioridad** | Baja |
| **Depende de** | — |
| **Referencias** | HU-32; HU-17, TK-043 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La moderación de un anuncio se llama «Retirar», un verbo que se confunde con «Eliminar» y «Marcar como finalizado».

**Objetivo:** llamar «Ocultar» a la moderación en todos los textos visibles, sin cambiar el comportamiento.

## 2. Alcance

**Incluye**
- Botón, diálogo de confirmación, avisos y página de anuncio no disponible.
- Parámetro de la URL `?retirado=1` → `?ocultado=1`.
- Mensaje `ListingLocked.RETIRED` de la API y su reconocimiento en `lockedMessage`.
- Pruebas y especificación `web-community-admin`.

**No incluye**
- Nombres internos (`hidden`, `RETIRED`), comentarios y tickets anteriores.

## 3. Requisitos técnicos

| Antes | Después |
|---|---|
| «Retirar anuncio» | «Ocultar anuncio» |
| «¿Retirar este anuncio?» / «Retirar» | «¿Ocultar este anuncio?» / «Ocultar» |
| «Anuncio retirado.» | «Anuncio ocultado.» |
| «Este anuncio está retirado y no se muestra en la comunidad.» | «Este anuncio está oculto y no se muestra en la comunidad.» |
| «…se haya eliminado o retirado.» | «…se haya eliminado u ocultado.» |
| «Este anuncio ha sido retirado por la administración de la comunidad.» | «Este anuncio ha sido ocultado por la administración de la comunidad.» |

## 4. Criterios de aceptación

**AC1 — Ocultar (HU-32 AC1)**
- **Given** un gestor ante un anuncio visible
- **When** pulsa «Ocultar anuncio»
- **Then** se le pide confirmar con «¿Ocultar este anuncio?» y «Ocultar»

**AC2 — Textos (HU-32 AC2)**
- **Given** un anuncio oculto
- **When** se vuelve al listado, se abre o el autor intenta editarlo
- **Then** los avisos hablan de «ocultar» y ningún texto visible dice «retirar»

## 5. Plan de tareas

1. Textos de la web y pruebas.
2. Mensaje de la API y pruebas.
3. Especificación.

## 6. Verificación

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
make build-frontend && $COMPOSE up -d web
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

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

- **Mensaje de la API:** la web reconoce el bloqueo por el texto (`/ocultado|finalizado/`); cambiarlo exige actualizar ambos lados a la vez.
