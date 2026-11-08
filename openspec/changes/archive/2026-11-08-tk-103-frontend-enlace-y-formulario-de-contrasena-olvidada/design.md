## Context

`LoginForm` es un formulario no controlado con `useActionState`: el correo escrito solo llega al servidor al enviar. El registro y el reenvío ya tratan el `503 email_quota_exceeded` (TK-099), y las páginas públicas de autenticación usan `AuthShell` y redirigen a `/inicio` con sesión.

## Goals / Non-Goals

**Goals:** enlace visible en el inicio de sesión y formulario para pedir el enlace sin revelar cuentas.

**Non-Goals:** la página para elegir la contraseña nueva (TK-104); límites por IP del proxy (TK-105).

## Decisions

- **`?email=` solo tras un intento fallido:** el enlace usa el correo que devuelve el estado de la acción (`state.values.email`), sin convertir el formulario en controlado. Es justo el caso en que el usuario descubre que no recuerda la contraseña. La cadena de consulta no se registra en el proxy ni en CloudFront (TK-091).
- **Mensaje de cupo propio:** el de registro habla de «correos de validación»; aquí se usa «Ahora mismo no podemos enviar correos. Inténtalo de nuevo en unos días.».
- **El aviso sustituye al formulario**, como el del registro, con un enlace «Volver a iniciar sesión»; el texto es el mismo exista o no la cuenta.
- **Componente `PasswordResetRequestForm` en `features/auth/components`** y la página solo compone: mismo reparto que `SignupForm` y `/registro`.
- **`429` del proxy, red o `5xx`:** «No hemos podido enviar el enlace. Inténtalo de nuevo en unos minutos.».

## Risks / Trade-offs

- [El correo viaja en la URL del enlace] → solo rellena el campo; no se envía a la API sin pulsar el botón y no queda en los registros.
