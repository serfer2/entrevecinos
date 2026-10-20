## Context

TK-009 dejó `requireUser()` y el proxy; TK-011 la página de perfil. TK-013 expone `POST /v1/communities` y `GET /v1/communities/{id}`.

## Goals / Non-Goals

**Goals:** crear una comunidad desde la interfaz y navegar entre secciones privadas.

**Non-Goals:** búsqueda y solicitudes (TK-016); edición.

## Decisions

- **El *layout* no comprueba la sesión:** solo pinta la cabecera; cada página llama a `requireUser()`.
- **`userApiFetch`** (`features/auth/api.ts`): añade el token de la *cookie* y redirige a `SESSION_EXPIRED_PATH` ante un `401`, para no repetir ese patrón en cada acción o página.
- **«Comunidades» apunta a `/comunidades/nueva`** hasta que TK-016 cree `/comunidades`.
- **Id no UUID en la URL → `notFound()`** sin llamar a la API.

## Risks / Trade-offs

- [Las páginas existentes usaban `min-h-screen`] → se ajustan para convivir con la cabecera.
