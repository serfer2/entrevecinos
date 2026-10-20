## Context

TK-024 expone `PATCH /v1/listings/{id}` y `PUT /v1/listings/{id}/images`; TK-023 dejó `ListingForm` e `ImagePicker`; TK-037 el detalle y `ListingActions`.

## Goals / Non-Goals

**Goals:** reutilizar el formulario; no confiar en valores del navegador; informar del fallo parcial.

**Non-Goals:** cambios de estado (TK-045).

## Decisions

- **Cambios calculados en el servidor:** la acción vuelve a leer el anuncio y compara (`listingChanges`, `imagesChanged`, funciones puras); sin cambios en los datos no llama al `PATCH`.
- **Precio:** se compara como número; quitarlo envía `price: null` (la API borra la moneda); ponerlo envía también `currency: "EUR"`.
- **Imágenes:** cambian si difiere el orden o si la portada actual no es la primera; la portada pasa a ser la primera del selector.
- **No autor → `Forbidden`** en la página, sin pintar el formulario; la API vuelve a comprobarlo al guardar.
- **Éxito → `/anuncios/<id>?actualizado=1`** con «Anuncio actualizado.».

## Risks / Trade-offs

- [`PATCH` + `PUT` no son atómicos] → mensaje específico si el segundo falla.
