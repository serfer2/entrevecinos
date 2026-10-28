# TK-069 · Frontend: visor de imágenes a pantalla completa

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`components/ui/Lightbox.tsx`, `features/listings/components/ListingGallery.tsx`, `styles/globals.css`) |
| **Historia** | HU-30 Ver las fotografías de un anuncio a pantalla completa (Épica 11) |
| **Prioridad** | Media |
| **Depende de** | TK-067 |
| **Referencias** | HU-30; TK-037 (detalle del anuncio) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

La galería del detalle muestra la imagen principal en media columna y miniaturas. No hay forma de ver una fotografía a mayor tamaño.

**Objetivo:** abrir las fotografías a pantalla completa y recorrerlas con botones, teclado o gestos táctiles.

## 2. Alcance

**Incluye**
- `Lightbox` genérico en un `<dialog>` modal.
- La imagen principal de `ListingGallery` pasa a ser un botón «Ampliar imagen N de M» con icono.
- Bloqueo del desplazamiento de la página con un diálogo modal abierto.

**No incluye**
- Zoom dentro de la imagen.
- Precarga de las imágenes vecinas.

## 3. Requisitos técnicos

### 3.1 Visor

- `showModal()`: atrapa el foco y lo devuelve al cerrar; Escape lo cierra.
- Fondo `gray-950` opaco; la imagen ocupa el espacio libre con `object-contain` (también amplía las pequeñas).
- Contador «N / M» (`aria-live`), «Cerrar», «Imagen anterior» e «Imagen siguiente» (sin flechas con una sola imagen).
- Comparte el índice con la galería: al cerrar, el detalle muestra la última imagen vista.

### 3.2 Gestos

- *Pointer events* con `touch-action: pan-y`: la imagen sigue al dedo y cambia con un desplazamiento horizontal de más de 50 px que supere al vertical.
- Los botones no capturan el puntero; tras arrastrar, el clic final no cierra el visor.
- `setPointerCapture` es opcional: si falla, el gesto sigue funcionando.

### 3.3 Pruebas

- Abrir y cerrar; botones y flechas del teclado (circular, sin doble avance); deslizar a ambos lados y movimiento corto; una sola imagen.

## 4. Criterios de aceptación

**AC1 — Ampliar (HU-30 AC1)**
- **Given** el detalle de un anuncio con fotografías
- **When** pulso la imagen principal
- **Then** la veo a pantalla completa con el contador y «Cerrar»

**AC2 — Carrusel (HU-30 AC2)**
- **Given** el visor abierto con varias imágenes
- **When** pulso las flechas, uso el teclado o deslizo el dedo
- **Then** cambio de imagen de forma circular

**AC3 — Cerrar (HU-30 AC3)**
- **Given** el visor abierto
- **When** pulso «Cerrar», Escape o el fondo
- **Then** vuelvo al detalle con la última imagen vista

## 5. Plan de tareas

1. `Lightbox` con pruebas.
2. Integración en `ListingGallery`.
3. Bloqueo del desplazamiento.
4. Verificación en escritorio y móvil.

## 6. Verificación

```bash
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
make build-frontend && $COMPOSE up -d web
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

Abrir el detalle de un anuncio con varias fotografías en escritorio y en un móvil.

## 7. Definición de terminado

- [ ] Los criterios de aceptación se cumplen.
- [ ] `lint`, `typecheck` y `test` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Pruebas táctiles:** el gesto se ha comprobado con eventos simulados; conviene probarlo en un móvil real.
