# web-password-reset Specification

## Purpose
Recuperación de la contraseña en la web (Épica 14): enlace desde el inicio de sesión, formulario para pedir el enlace y, con TK-104, página para elegir la contraseña nueva.
## Requirements
### Requirement: Enlace de contraseña olvidada en el inicio de sesión
El formulario de `/iniciar-sesion` SHALL mostrar el enlace «¿Has olvidado tu contraseña?» a `/recuperar-contrasena`. Si el estado del formulario conserva un correo tras un intento fallido, el enlace SHALL incluirlo como `?email=<correo>`.

#### Scenario: Enlace visible
- **WHEN** un visitante abre `/iniciar-sesion`
- **THEN** ve «¿Has olvidado tu contraseña?» y el enlace lleva a `/recuperar-contrasena`

#### Scenario: Correo del intento fallido
- **WHEN** el inicio de sesión falla con el correo `vecino@example.com`
- **THEN** el enlace lleva a `/recuperar-contrasena?email=vecino%40example.com`

### Requirement: Pedir el enlace desde la web
`/recuperar-contrasena` SHALL ser una página pública con el título «Recupera tu contraseña», un campo «Correo electrónico» (rellenado con `?email=` si viene) y el botón «Enviar enlace»; con sesión iniciada SHALL redirigir a `/inicio`. La Server Action `requestPasswordReset` SHALL validar el correo antes de llamar a `POST /v1/auth/password-reset`. Con `202`, el formulario SHALL sustituirse por un aviso `role="status"`: «Si hay una cuenta con ese correo, te hemos enviado un enlace para restablecer la contraseña. Caduca en 1 hora.», con un enlace «Volver a iniciar sesión». Con `503` y `code: email_quota_exceeded` SHALL mostrar «Ahora mismo no podemos enviar correos. Inténtalo de nuevo en unos días.»; con `422`, el error junto al campo; con cualquier otro error, «No hemos podido enviar el enlace. Inténtalo de nuevo en unos minutos.». En los errores SHALL conservar el correo escrito.

#### Scenario: Enlace pedido
- **WHEN** se envía el formulario con un correo válido y la API responde `202`
- **THEN** se ve el aviso, igual exista o no la cuenta

#### Scenario: Correo no válido
- **WHEN** se envía el formulario con `no-es-un-correo`
- **THEN** se ve «Introduce un correo electrónico válido.» y no se llama a la API

#### Scenario: Sin cupo
- **WHEN** la API responde `503` con `code: email_quota_exceeded`
- **THEN** se ve el mensaje de cupo y el correo sigue escrito

### Requirement: Recibir el enlace sin el token en la URL
`GET /restablecer-contrasena/enlace?token=<token>` SHALL guardar el *token* en la *cookie* `ev_password_reset` (`HttpOnly`, `SameSite=Lax`, `Secure` en producción, `Path=/restablecer-contrasena`, `Max-Age` 3600) y redirigir con `303` a `/restablecer-contrasena`. MUST NOT llamar a la API. Sin `token` SHALL redirigir a `/restablecer-contrasena?motivo=invalido`. La respuesta SHALL llevar `Cache-Control: no-store` y `Referrer-Policy: no-referrer`. Ambas rutas SHALL ser públicas.

#### Scenario: Enlace del correo
- **WHEN** se abre el enlace del correo
- **THEN** la barra de direcciones muestra `/restablecer-contrasena` sin el *token* y se ve el formulario

#### Scenario: Enlace sin token
- **WHEN** se abre `/restablecer-contrasena/enlace` sin `token`
- **THEN** se ve «El enlace para restablecer la contraseña no es válido.»

### Requirement: Elegir la contraseña nueva
Con la *cookie*, `/restablecer-contrasena` SHALL mostrar «Contraseña nueva» y «Repite la contraseña» (`autocomplete="new-password"`, de 12 a 128 caracteres) y el botón «Cambiar contraseña». Si no coinciden, SHALL mostrar «Las contraseñas no coinciden.» sin llamar a la API. La Server Action `resetPassword` SHALL enviar el *token* de la *cookie* y la contraseña a `POST /v1/auth/password-reset/confirm`. Con `204` SHALL borrar la *cookie* y la sesión y redirigir a `/iniciar-sesion?motivo=contrasena-cambiada`, que muestra «Tu contraseña se ha cambiado. Inicia sesión con la nueva.». Con `422` SHALL marcar la contraseña; con otro error, «No hemos podido cambiar la contraseña. Inténtalo de nuevo en unos minutos.».

#### Scenario: Contraseña cambiada
- **WHEN** se envían dos contraseñas iguales y válidas y la API responde `204`
- **THEN** se llega al inicio de sesión con el aviso de contraseña cambiada

#### Scenario: Contraseñas distintas
- **WHEN** las dos contraseñas no coinciden
- **THEN** se ve «Las contraseñas no coinciden.» y no se llama a la API

### Requirement: Enlace caducado o no válido en la web
Sin la *cookie* o con `motivo=invalido`, la página SHALL mostrar «El enlace para restablecer la contraseña no es válido. Puede que ya lo hayas usado o que hayas pedido otro más reciente.»; con `motivo=caducado`, «El enlace para restablecer la contraseña ha caducado.». En ambos casos SHALL ofrecer «Pedir otro enlace» a `/recuperar-contrasena`. Si la API responde `410` o `400` al enviar el formulario, la acción SHALL borrar la *cookie* y mostrar el mensaje correspondiente con el mismo enlace.

#### Scenario: Enlace caducado al enviar
- **WHEN** la API responde `410` con `code: password_reset_expired`
- **THEN** se ve el mensaje de enlace caducado y «Pedir otro enlace»

#### Scenario: Enlace ya usado
- **WHEN** la API responde `400` con `code: password_reset_invalid`
- **THEN** se ve el mensaje de enlace no válido y «Pedir otro enlace»

