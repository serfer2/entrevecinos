## Context

Las páginas de servidor no pueden escribir *cookies*; la validación tiene que crear la sesión.

## Decisions

- **`/verificar-correo` es un *route handler* `GET`** que llama a `POST /v1/auth/email-verification` y redirige; responde con `Referrer-Policy: no-referrer` y `Cache-Control: no-store` para que el token no se filtre.
- **Enlace repetido (`400`) no es un error para el usuario:** con sesión sigue a `/comunidades`; sin ella, `/iniciar-sesion?motivo=correo-validado`. Cubre el doble clic y los escáneres de correo.
- **`errorCodeOf`** lee el `code` del cuerpo del error de la API.
- **Huecos para el reenvío** (TK-061): `emailNotVerified` en el estado del inicio de sesión y el `email` en la URL de la página de enlace caducado.

## Risks / Trade-offs

- [El correo viaja en la *query* de la página de error] → no es un secreto, pero queda en el historial.
