# TK-066 · Frontend: tema visual inspirado en la naturaleza y tipografía

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / diseño |
| **Componente** | `apps/web/` (`src/styles/globals.css`, `src/app/layout.tsx`, `src/components/brand/`) |
| **Historia** | HU-28 Usar una interfaz sencilla, clara y con identidad propia (Épica 11) |
| **Prioridad** | Media |
| **Depende de** | — |
| **Referencias** | `readme.md` §1.3; Tailwind CSS v4 (`@theme`); `next/font` |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

Toda la interfaz usa utilidades de Tailwind en línea sobre las paletas `emerald`, `gray`, `amber` y `red`, con los colores por defecto y la fuente del sistema. `globals.css` solo importa Tailwind. El resultado es correcto pero genérico, sin identidad propia.

**Objetivo:** definir la identidad visual de EntreVecinos en un único sitio para que todas las páginas cambien a la vez, sin renombrar clases ni tocar la lógica.

## 2. Alcance

**Incluye**
- Redefinir en `@theme` las paletas `emerald` (verde musgo), `gray` (neutros cálidos de piedra y tierra), `amber` (ocre) y `red` (terracota).
- Tipografías Figtree (texto) y Fraunces (títulos), autoalojadas con `next/font`.
- Estilos base: fondo de página, títulos, subrayado de enlaces, foco visible y selección.
- Logotipo `BrandMark` (brote + nombre).

**No incluye**
- Cambios de estructura de las páginas (TK-067).

## 3. Requisitos técnicos

### 3.1 Paletas

| Paleta | Uso | Tono de referencia |
|---|---|---|
| `emerald` | Acción principal, enlaces, precio, estado actual | `emerald-700` `#3d5a2f` |
| `gray` | Texto, bordes, fondos | `gray-50` `#f8f6f0` (fondo de página) |
| `amber` | Avisos, «Reservado» | `amber-100`/`amber-900` |
| `red` | Errores y acciones destructivas | `red-700` `#8d3a25` |

- Los tonos 600 o superiores mantienen contraste AA sobre blanco y sobre `gray-50`.

### 3.2 Tipografía

- `Figtree` como `--font-sans` y `Fraunces` (eje `SOFT`) como `--font-display`, aplicada a `h1` y `h2`.
- Autoalojadas por `next/font`: la CSP (`font-src 'self'`) no cambia. La compilación necesita acceso a Internet para descargarlas (asumido).

### 3.3 Logotipo

- `BrandMark` (`md` y `lg`): icono decorativo (`aria-hidden`) y el nombre como texto.

## 4. Criterios de aceptación

**AC1 — Identidad en todas las páginas (HU-28 AC1)**
- **Given** cualquier página de la aplicación
- **When** la abro
- **Then** uso la paleta, la tipografía y el logotipo nuevos, con contraste AA

**AC2 — Foco visible**
- **Given** que navego con el teclado
- **When** paso por enlaces y botones
- **Then** el elemento enfocado muestra un contorno verde

## 5. Plan de tareas

1. Paletas y estilos base en `globals.css`.
2. Fuentes en el *layout* raíz.
3. `BrandMark`.
4. Verificación visual en escritorio y móvil.

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

- **Paletas redefinidas:** se mantienen los nombres de Tailwind (`emerald`, `gray`…) para no tocar cientos de clases; el nombre ya no describe el color exacto.
- **Descarga de fuentes:** `next build` descarga las fuentes de Google; sin red, la compilación falla.
