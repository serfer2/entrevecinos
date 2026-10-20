## Context

TK-036 expone `GET /v1/listings/{id}` (403/404 según la visibilidad). TK-029 dejó `ListingCard` y los formateadores.

## Goals / Non-Goals

**Goals:** detalle completo, galería con teclado, mensajes claros de no disponible y sin acceso.

**Non-Goals:** contacto (TK-039) y acciones (TK-025, TK-027, TK-043, TK-045).

## Decisions

- **Datos en paralelo:** anuncio, categorías y comunidad; mi membresía para calcular `canModerate`.
- **`ListingGallery` (cliente):** imagen principal (portada) y miniaturas como botones con `aria-pressed`; flechas izquierda/derecha cambian de imagen; «Imagen N de M» anunciado con `aria-live`.
- **`ListingActions`** recibe `isOwner`, `canModerate` y el anuncio; hoy no pinta nada.
- **«Actualizado el …»** solo si `updated_at` supera a `published_at` en más de un minuto.
- **`CurrentUser` incluye `platform_role`** para saber si puede moderar en cualquier comunidad (la API sigue decidiendo).

## Risks / Trade-offs

- [Un enlace compartido fuera de la comunidad] → quien no es miembro ve el aviso de acceso.
