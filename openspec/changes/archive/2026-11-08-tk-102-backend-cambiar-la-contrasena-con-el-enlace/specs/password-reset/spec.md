## ADDED Requirements

### Requirement: Cambiar la contraseña con el enlace
`POST /v1/auth/password-reset/confirm` SHALL ser público y aceptar `{"token": "...", "password": "..."}` (`additionalProperties: false`; `password` de 12 a 128 caracteres). Con un enlace vigente de una cuenta que puede restablecer su contraseña, SHALL guardar el hash de la contraseña nueva, fijar `users.password_changed_at`, borrar todos los enlaces del usuario y responder `204` sin emitir ningún JWT. Si la cuenta no había validado su correo, SHALL quedar validada y activa.

#### Scenario: Enlace vigente
- **WHEN** se confirma con un enlace emitido hace menos de 60 minutos y una contraseña válida
- **THEN** la respuesta es `204`, la contraseña nueva inicia sesión, la antigua no y el enlace deja de valer

#### Scenario: Cuenta sin validar
- **WHEN** una cuenta pendiente de validar su correo confirma con su enlace
- **THEN** queda validada y activa y puede iniciar sesión con la contraseña nueva

#### Scenario: Contraseña no válida
- **WHEN** se confirma con una contraseña de menos de 12 caracteres
- **THEN** la respuesta es `422` y el enlace sigue valiendo

### Requirement: Enlace caducado o no válido
Un enlace caducado SHALL responder `410` con `{"detail": "El enlace para restablecer la contraseña ha caducado.", "code": "password_reset_expired"}`. Un enlace desconocido, ya usado, sustituido por otro o de una cuenta que ya no puede restablecer su contraseña SHALL responder `400` con `{"detail": "El enlace para restablecer la contraseña no es válido.", "code": "password_reset_invalid"}`. En ambos casos la contraseña MUST NOT cambiar.

#### Scenario: Enlace caducado
- **WHEN** se confirma con un enlace emitido hace más de 60 minutos
- **THEN** la respuesta es `410` con `code: password_reset_expired`

#### Scenario: Enlace usado o sustituido
- **WHEN** se confirma con un enlace ya usado o anterior al último pedido
- **THEN** la respuesta es `400` con `code: password_reset_invalid`

### Requirement: Aviso del cambio de contraseña
Tras un cambio correcto, la API SHALL enviar en segundo plano un correo con asunto «Tu contraseña de EntreVecinos ha cambiado», con la fecha y la hora del cambio en hora de Madrid, que consume una plaza del cupo de correos. Sin cupo, la contraseña MUST cambiar igual y el aviso MUST NOT enviarse.

#### Scenario: Aviso enviado
- **WHEN** se cambia la contraseña con el enlace
- **THEN** la cuenta recibe el aviso del cambio

#### Scenario: Sin cupo
- **WHEN** se cambia la contraseña con el cupo agotado
- **THEN** la respuesta es `204`, la contraseña cambia y no se envía el aviso
