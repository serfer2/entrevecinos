## ADDED Requirements

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
