# TK-023 · Frontend: publicar un anuncio con fotografías

| Campo | Valor |
|---|---|
| **Tipo** | Frontend / funcionalidad |
| **Componente** | `apps/web/` (`features/listings/`, `features/media/`, `app/(privado)/comunidades/[communityId]/anuncios/nuevo/`, `app/media/[assetId]/route.ts`) |
| **Historia** | HU-07 Publicar un anuncio (Épica 3) |
| **Prioridad** | Alta |
| **Depende de** | TK-016, TK-021, TK-022 |
| **Referencias** | `user-stories.md` HU-07; `docs/api/paths/media.yaml`, `media_asset_id.yaml`, `categories.yaml`, `communities_community_id_listings.yaml` (`post`) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

HU-07 pide un formulario para publicar un anuncio con título, descripción, categoría, tipo, precio opcional y fotografías. El navegador no tiene el token (está en la *cookie* `httpOnly`, TK-007), así que ni la subida de imágenes ni su lectura pueden ir directas del navegador a la API.

**Objetivo:** crear la página `/comunidades/[communityId]/anuncios/nuevo`, la subida de fotografías a través del servidor de Next y la ruta `/media/[assetId]` que sirve las imágenes al navegador.

## 2. Alcance

**Incluye**
- Ruta `app/media/[assetId]/route.ts` (proxy de lectura de imágenes).
- *Server Action* `uploadImage` (una imagen por llamada) y componente `ImagePicker`.
- `listingSchema`, *Server Action* `publishListing`, `ListingForm` (reutilizable en TK-025).
- Etiquetas en español de los tipos de anuncio (`features/listings/labels.ts`).
- Botón «Publicar anuncio» en la página de la comunidad, solo para miembros aprobados.

**No incluye**
- Listado de anuncios (TK-029) y detalle (TK-037). Tras publicar se vuelve a la página de la comunidad.

## 3. Requisitos técnicos

### 3.1 Lectura de imágenes: `GET /media/[assetId]`

- *Route Handler* de Next: valida que `assetId` es un UUID, lee el token de la *cookie* y llama a `GET /v1/media/{id}` **sin seguir la redirección** (`redirect: "manual"`).
- `302` de la API → responde `302` con el mismo `Location` (URL prefirmada de MinIO) y `Cache-Control: private, max-age=240`.
- `401` → `401`; `403`/`404` → `404` (no revela qué imágenes existen). Sin *cookie*, el proxy de TK-009 ya redirige; la ruta está fuera de `PUBLIC_ROUTES`.
- Las URLs de imagen del API (`/v1/media/<id>`) se traducen en el frontend a `/media/<id>` con una función `mediaSrc(url)`.
- El origen final de las imágenes es el del almacenamiento (`STORAGE_PUBLIC_URL`), no el de Next: cualquier CSP debe incluirlo en `img-src` (TK-046).
- Las imágenes se muestran con `<img>` (y `loading="lazy"`, `alt` descriptivo); `next/image` no aporta aquí porque las URL prefirmadas cambian en cada petición (asumido; desactivar la regla `@next/next/no-img-element` solo en el componente `ListingImage`).

### 3.2 Subida: *Server Action* `uploadImage(formData)`

- Una imagen por llamada, para no superar el límite del cuerpo de las *Server Actions*: `next.config.ts` → `experimental.serverActions.bodySizeLimit = "6mb"` (asumido; comprobar el nombre exacto de la opción en la documentación de Next 16 incluida en `node_modules/next/dist/docs/`).
- Comprobación previa en el servidor de Next: tamaño ≤ 5 MB y `type` en JPEG/PNG/WebP (la API vuelve a validar el contenido real).
- Reenvía a `POST /v1/media` como `multipart/form-data`: ampliar `apiFetch` para aceptar `FormData` (sin `Content-Type`, lo pone `fetch`).
- Devuelve `{ id, url }` o un error: `413` → «La imagen supera 5 MB.», `415` → «Formato no permitido. Usa JPEG, PNG o WebP.».

### 3.3 `ImagePicker`

- `<input type="file" accept="image/jpeg,image/png,image/webp" multiple>` con etiqueta «Fotografías (hasta 10)».
- Al elegir ficheros: valida en el cliente tamaño y tipo, y llama a `uploadImage` para cada uno (en serie), mostrando el progreso por fichero («Subiendo…», error, miniatura).
- Lista de miniaturas con «Quitar» y botones para mover arriba o abajo; la primera es la portada («Portada»).
- Guarda los ids en campos ocultos `image_asset_ids` en el orden mostrado. Máximo 10.
- Accesible con teclado; los errores por fichero se anuncian con `aria-live="polite"`.

### 3.4 `listingSchema` y `ListingForm`

| Campo | Regla | Mensaje |
|---|---|---|
| `title` | se recorta; 1–160 | «El título es obligatorio.» / «Máximo 160 caracteres.» |
| `description` | se recorta; 1–5000 | «La descripción es obligatoria.» / «Máximo 5000 caracteres.» |
| `category_id` | UUID de la lista | «Elige una categoría.» |
| `type` | uno de `ListingType` | «Elige el tipo de anuncio.» |
| `price` | opcional; número ≥ 0 con hasta 2 decimales; admite coma decimal («12,50») | «Introduce un precio válido.» |

- Tipos en un grupo de botones de radio con las etiquetas del README: Vendo (`sell`), Busco (`wanted`), Ofrezco (`offer_service`), Necesito (`need_service`), Regalo (`free`), Otros (`other`).
- Categorías: `<select>` con `GET /v1/categories`.
- Precio con el sufijo «€»; se envía `currency: "EUR"` solo si hay precio. Si el tipo es «Regalo», se muestra la ayuda «Normalmente sin precio» (asumido).

### 3.5 *Server Action* `publishListing`

- `requireUser()`; valida; `POST /v1/communities/{id}/listings` con `image_asset_ids`.
- `201` → `redirect("/comunidades/<communityId>?publicado=1")`, que muestra «Anuncio publicado.».
- `403` → aviso de acceso (pendiente o sin acceso). `400` → «Alguna fotografía no es válida. Vuelve a subirla.». `422` → errores por campo. Red o `5xx` → error general.
- Se conservan los valores (y las imágenes ya subidas) cuando hay error.

### 3.6 Pruebas

- `listingSchema` (precio con coma, negativo, tres decimales; campos obligatorios).
- `uploadImage` y `publishListing` con `apiFetch` simulado.
- Ruta `/media/[assetId]`: `302` reenviado, `403` → `404`, id inválido.
- `ImagePicker`: añadir, quitar, reordenar, límite de 10, error de tamaño.

## 4. Criterios de aceptación

**AC1 — Publicación correcta (HU-07 AC1)**
- **Given** que soy miembro aprobado y estoy en la página de mi comunidad
- **When** pulso «Publicar anuncio», completo título, descripción, categoría y tipo, y publico
- **Then** vuelvo a la comunidad con «Anuncio publicado.»

**AC2 — Precio opcional (HU-07 AC2)**
- **Given** el formulario
- **When** publico un «Regalo» sin precio
- **Then** se publica sin precio ni moneda

**AC3 — Fotografías (HU-07 AC3)**
- **Given** el formulario
- **When** adjunto tres fotografías, cambio su orden y publico
- **Then** el anuncio se crea con ese orden y la primera como portada; las miniaturas se ven a través de `/media/<id>`

**AC4 — Validación (HU-07 AC4)**
- **Given** el formulario
- **When** publico sin título, descripción, categoría o tipo (incluso sin validación del navegador), o adjunto un fichero de 6 MB o un PDF
- **Then** veo el error junto a cada campo o fichero y no se publica nada

**AC5 — Sin acceso aprobado (HU-07 AC5)**
- **Given** que mi solicitud está pendiente
- **When** abro la página de la comunidad o la URL `/anuncios/nuevo`
- **Then** no veo el botón «Publicar anuncio» y la URL muestra el aviso de solicitud pendiente

## 5. Plan de tareas

1. `apiFetch` con `FormData` y la ruta `/media/[assetId]`.
2. `uploadImage`, `bodySizeLimit` e `ImagePicker`.
3. `labels.ts`, `listingSchema`, `ListingForm` y `publishListing`.
4. Página `/anuncios/nuevo` y botón en la comunidad.
5. Pruebas y verificación según la sección 6.

## 6. Verificación

```bash
make dev
# Miembro aprobado: /comunidades/<id> → «Publicar anuncio» → completar, 3 fotos, reordenar → publicar
# Comprobar en la API: GET /v1/communities/<id>/listings (TK-028) o la base de datos
# Subir un PDF renombrado y una foto de 6 MB → errores por fichero
# DevTools > Red: las imágenes se piden a /media/<id> → 302 a localhost:9000 (sin token en la URL del navegador hacia la API)
COMPOSE="docker compose --env-file .env -f infra/docker-compose.yml"
$COMPOSE exec web npm run lint && $COMPOSE exec web npm run typecheck && $COMPOSE exec web npm run test
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] El token nunca sale del servidor de Next, tampoco para las imágenes.
- [ ] El formulario es usable con teclado y en móvil.
- [ ] `lint`, `typecheck`, `test` y `build` pasan.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Subidas en serie:** más lentas que en paralelo, pero sencillas y con menos carga; revisar si molesta.
- **Imágenes subidas y no publicadas:** quedan huérfanas (TK-021 §8).
- **CSP:** las imágenes llegan por una redirección a `localhost:9000` (S3 en producción), así que la `Content-Security-Policy` debe permitir ese origen en `img-src`. Lo resuelve TK-046, que debe completarse antes de cerrar la Épica 3; mientras no exista CSP, nada bloquea las imágenes.
