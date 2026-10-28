# TK-068 · Frontend: campos de formulario proporcionados en Firefox

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / corrección |
| **Componente** | `apps/web/` (`components/ui/TextField.tsx`, `SelectField.tsx`, `TextAreaField.tsx`, `app/(privado)/comunidades/page.tsx`, `features/listings/components/ListingFilters.tsx`, `ListingForm.tsx`) |
| **Historia** | HU-29 Usar los formularios correctamente en cualquier navegador (Épica 11) |
| **Prioridad** | Media |
| **Depende de** | TK-067 |
| **Referencias** | HU-29 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

En Firefox, el ancho natural de un `<input>` es mayor que en Chrome. Las columnas `fr` de una rejilla no bajan de ese ancho, así que el buscador de comunidades se sale de su panel. Al corregirlo con `w-full`, el campo de precio, dentro de un contenedor `flex-1`, pasa a ocupar todo el ancho, y el «€» se alinea con la ayuda en lugar de con el importe.

**Objetivo:** que los campos se ajusten a su columna en cualquier navegador y que el precio tenga un ancho proporcionado.

## 2. Alcance

**Incluye**
- Columnas `minmax(0, …)` en el buscador de comunidades y en los filtros de anuncios.
- `w-full min-w-0` en `TextField`, `SelectField` y `TextAreaField`.
- Propiedad `suffix` en `TextField` (unidad dentro del campo, decorativa).
- Precio con `suffix="€"` y `max-w-xs`.

**No incluye**
- Otros navegadores no soportados por Next.js.

## 3. Requisitos técnicos

- `suffix` es `aria-hidden`: la unidad la explica la ayuda del campo («En euros…»).
- El campo reserva espacio a la derecha (`pr-9`) cuando lleva sufijo.

## 4. Criterios de aceptación

**AC1 — Buscador de comunidades (HU-29 AC1)**
- **Given** Firefox en escritorio
- **When** abro `/comunidades`
- **Then** los tres campos y «Buscar» caben dentro del panel

**AC2 — Precio (HU-29 AC2)**
- **Given** Firefox
- **When** publico o edito un anuncio
- **Then** el precio mide como mucho 20 rem y muestra «€» dentro, alineado con el importe

## 5. Plan de tareas

1. Rejillas con `minmax(0, …)`.
2. Ancho de los campos.
3. `suffix` y campo de precio.
4. Comprobación en Firefox.

## 6. Verificación

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
make build-frontend && $COMPOSE up -d web
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

Abrir `/comunidades` y `/comunidades/<id>/anuncios/nuevo` en Firefox.

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck` y `test` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Ancho máximo del precio:** 20 rem deja sitio a la ayuda sin partirla en dos líneas (asumido).
