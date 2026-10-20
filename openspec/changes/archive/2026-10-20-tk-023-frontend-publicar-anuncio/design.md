## Context

TK-021 expone `POST /v1/media` y `GET /v1/media/{id}` (302); TK-022 `GET /v1/categories` y `POST /v1/communities/{id}/listings`.

## Goals / Non-Goals

**Goals:** el token nunca sale del servidor de Next; subir y ordenar fotos con teclado; conservar lo escrito y las fotos ante errores.

**Non-Goals:** listado y detalle de anuncios (TK-029, TK-037); CSP (TK-046).

## Decisions

- **`/media/[assetId]` como *Route Handler*:** llama a la API con `redirect: "manual"` y reenvía el `Location`; `403`/`404` → `404` para no revelar qué imágenes existen.
- **Una imagen por *Server Action*:** evita superar el límite del cuerpo; `experimental.serverActions.bodySizeLimit = "6mb"` (5 MB + margen del multipart, según la documentación de Next 16).
- **`ImagePicker` llama a `uploadImage` directamente** (las *Server Actions* se pueden invocar desde el cliente), en serie; guarda los ids en campos ocultos `image_asset_ids` en el orden mostrado y avisa al formulario mientras sube para deshabilitar «Publicar».
- **Precio como texto normalizado** (`"12,50"` → `"12.50"`): la API lo trata como `Decimal` sin pasar por `float`.
- **`ApiError.payload`** con el cuerpo del error para leer el `status` de los `403` de membresía.
- **`<img>` en lugar de `next/image`:** las URL prefirmadas cambian en cada petición.

## Risks / Trade-offs

- [Subidas en serie] → más lentas, pero sencillas.
- [Imágenes subidas y no publicadas quedan huérfanas] → limpieza posterior (TK-021 §8).
