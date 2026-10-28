# TK-067 · Frontend: rediseño de páginas y componentes

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / diseño |
| **Componente** | `apps/web/` (páginas de `app/`, `components/ui/`, `features/*/components/`) |
| **Historia** | HU-28 Usar una interfaz sencilla, clara y con identidad propia (Épica 11) |
| **Prioridad** | Media |
| **Depende de** | TK-066 |
| **Referencias** | `readme.md` §1.3; HU-10, HU-11, HU-12, HU-14 |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Con el tema de TK-066 los colores cambian, pero la estructura sigue siendo la de un prototipo: formularios sin superficie, tarjetas planas, filtros dispersos y páginas públicas sin marca.

**Objetivo:** ordenar la jerarquía visual de las páginas y destacar lo importante de cada anuncio.

## 2. Alcance

**Incluye**
- `AuthShell`: marco común de inicio de sesión, registro y error de validación del correo.
- Cabecera privada con el logotipo (fija desde `sm`) y pie de página.
- `ListingCard`: imagen, tipo sobre la imagen, «Reservado» en ocre, título y precio destacado.
- Búsqueda, filtros y orden en un panel con icono de lupa.
- Listas, formularios y paneles sobre superficies blancas (`rounded-2xl`); radio único `rounded-lg` en controles.
- Estado vacío del listado y cabecera de la comunidad con ubicación.
- Detalle del anuncio: etiquetas en píldora, precio destacado, galería y anunciante en paneles.

**No incluye**
- Visor de imágenes (TK-069).
- Cambios de funcionalidad o de textos de negocio.

## 3. Requisitos técnicos

- Iconos solo donde ayudan a entender una acción: lupa (búsqueda), ubicación (comunidad) y la marca.
- Animaciones (elevación de la tarjeta y zoom de la imagen) desactivadas con `prefers-reduced-motion`.
- Rejilla del listado: 1 columna en móvil, 2 desde 420 px, 3 en `md` y 4 en `lg`.
- La cabecera solo es fija desde `sm` para no ocupar pantalla en móvil.

## 4. Criterios de aceptación

**AC1 — Tarjetas (HU-28 AC2)**
- **Given** el listado de una comunidad
- **When** recorro los anuncios
- **Then** cada tarjeta destaca fotografía, título y precio, con el tipo y «Reservado» sobre la imagen

**AC2 — Panel de búsqueda (HU-28 AC3)**
- **Given** el listado de una comunidad
- **When** busco o filtro
- **Then** búsqueda, tipo, categoría y orden están en un mismo panel

**AC3 — Móvil (HU-28 AC4)**
- **Given** un móvil de 390 px
- **When** abro el listado o el detalle
- **Then** no hay desplazamiento horizontal y la cabecera no queda fija

## 5. Plan de tareas

1. `AuthShell` y páginas públicas.
2. Cabecera, pie y `NavLink`.
3. `ListingCard`, `ListingFilters`, `CommunityListings`, paginación.
4. Páginas de comunidad, inicio, buscador, detalle y formularios.
5. Verificación visual en escritorio y móvil.

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

- **Sin pruebas visuales automáticas:** el aspecto se ha comprobado a mano; las pruebas existentes cubren el comportamiento.
