## ADDED Requirements

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
