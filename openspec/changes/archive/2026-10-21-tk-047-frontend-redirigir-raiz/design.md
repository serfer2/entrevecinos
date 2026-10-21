## Context

`/` está en `PUBLIC_ROUTES`, así que el proxy no la redirige. `/iniciar-sesion` y `/registro` ya comprueban la sesión con `getCurrentUser()` (DAL de TK-009) y tratan un fallo de la API como sin sesión.

## Decisions

- **Redirección en la página, no en el proxy:** el proxy solo mira si existe la *cookie*; la página valida el token con el DAL y evita mandar a `/inicio` a quien tiene una *cookie* caducada.
- **API caída = sin sesión** (`.catch(() => null)`), igual que en `/iniciar-sesion`: lleva al formulario en lugar de mostrar un error.
- **Sin prueba unitaria:** la página solo encadena `getCurrentUser()` y `redirect()`; se verifica contra el servicio levantado.

## Risks / Trade-offs

- [Sin página de bienvenida para visitantes] → si se quiere presentar EntreVecinos, `/` necesitará su propia historia.
