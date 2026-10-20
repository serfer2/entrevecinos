## Context

TK-008 expone `POST /v1/auth/token` y `GET /v1/users/me`. TK-007 guarda el JWT en `ev_session`.

## Goals / Non-Goals

**Goals:** rutas privadas por defecto; verificación real del token en el servidor; sin bucles de redirección; sin *open redirect*.

**Non-Goals:** cierre de sesión, recuperación de contraseña, páginas de comunidades.

## Decisions

- **Dos niveles:** `proxy.ts` solo comprueba la existencia de la *cookie* (rápido, sin red); el DAL valida el token llamando a `/users/me` (una vez por petición gracias a `cache` de React).
- **Lista blanca de rutas públicas** (`/`, `/registro`, `/iniciar-sesion`): toda ruta nueva queda protegida sin configuración.
- **Sin redirección «fuera del login» en el proxy:** con una *cookie* caducada provocaría un bucle; la decide la página con el DAL.
- **`SESSION_COOKIE` en `routes.ts`:** el proxy no puede importar `session.ts` (`server-only` + `next/headers`).
- **`safeNextPath`:** exige `/` inicial, rechaza `//`, `\`, caracteres de control y cualquier valor que, resuelto contra un origen ficticio, cambie de origen.
- **Páginas públicas toleran fallos de la API:** si `getCurrentUser()` falla por red, se muestra el formulario igualmente.
- **Pruebas de proxy, DAL y acciones en entorno `node`** (`NextRequest` y `Response` nativos).

## Risks / Trade-offs

- [Una llamada a `/users/me` por petición privada] → aceptable en el MVP.
- [La *cookie* inválida no se borra al renderizar] → se sobrescribe al iniciar sesión y caduca por `maxAge`.
