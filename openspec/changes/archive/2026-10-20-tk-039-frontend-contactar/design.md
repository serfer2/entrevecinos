## Context

TK-038 añadió `ListingOwner.email`; TK-037 el detalle, que ya muestra el aviso de acceso (sin datos) cuando la API responde 403.

## Decisions

- **`<details>`/`<summary>`** para desplegar el contacto: accesible y sin JavaScript. Es presentación, no protección: los datos solo llegan si la API los autorizó.
- **Teléfono primero**; `tel:` sin espacios ni separadores; asunto del correo con `encodeURIComponent`.

## Risks / Trade-offs

- [Sin preferencias de privacidad del anunciante] → post-MVP.
