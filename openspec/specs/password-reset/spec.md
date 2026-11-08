# password-reset Specification

## Purpose
Recuperación de la contraseña olvidada (Épica 14): petición del enlace por correo sin revelar qué correos están registrados, enlaces de un solo uso y límites contra abusos y por coste.
## Requirements
### Requirement: Pedir el enlace para restablecer la contraseña
`POST /v1/auth/password-reset` SHALL ser público y aceptar `{"email": "..."}` (`additionalProperties: false`). Si el correo, normalizado, pertenece a una cuenta no borrada que está activa o pendiente de validar su correo, SHALL enviar en segundo plano un correo con el enlace `{WEB_PUBLIC_URL}/restablecer-contrasena/enlace?token=<token>`, válido `PASSWORD_RESET_TTL_MINUTES` minutos (60 por defecto). SHALL responder siempre `202` con `{"detail": "Si hay una cuenta con ese correo, te enviaremos un enlace para restablecer la contraseña."}`, exista o no la cuenta. Un cuerpo no válido SHALL responder `422`.

#### Scenario: Cuenta activa
- **WHEN** se pide el enlace con el correo de una cuenta activa
- **THEN** la respuesta es `202` y se envía un correo con asunto «Restablece tu contraseña de EntreVecinos» y el enlace

#### Scenario: Correo sin cuenta
- **WHEN** se pide el enlace con un correo que no está registrado
- **THEN** la respuesta es la misma `202` y no se envía nada

#### Scenario: Cuenta borrada o desactivada
- **WHEN** se pide el enlace con el correo de una cuenta borrada o desactivada con el correo ya validado
- **THEN** la respuesta es `202` y no se envía nada

#### Scenario: Cuenta pendiente de validar
- **WHEN** se pide el enlace con el correo de una cuenta que todavía no ha validado su correo
- **THEN** la respuesta es `202` y se envía el enlace

### Requirement: Enlaces de un solo uso y sin abusos
Solo SHALL guardarse el SHA-256 del *token*. Emitir un enlace MUST borrar los anteriores del usuario, de modo que solo vale el último. Si el último enlace del usuario se creó hace menos de 60 segundos, la petición MUST NOT enviar otro correo.

#### Scenario: Enlace nuevo sustituye al anterior
- **WHEN** se pide un enlace pasados 60 segundos desde el anterior
- **THEN** se envía uno nuevo y el anterior deja de existir

#### Scenario: Dos peticiones seguidas
- **WHEN** se pide el enlace dos veces en menos de 60 segundos
- **THEN** solo se envía un correo

### Requirement: Cupo de correos al pedir el enlace
La petición MUST comprobar el cupo de correos del periodo antes de buscar la cuenta: sin cupo SHALL responder `503` con `code: email_quota_exceeded` y `Retry-After`, exista o no la cuenta. Cada enlace enviado SHALL consumir una plaza del cupo; una petición que no envía nada MUST NOT consumirla.

#### Scenario: Sin cupo
- **WHEN** se pide el enlace con el cupo agotado, con un correo registrado o sin registrar
- **THEN** la respuesta es `503` con `code: email_quota_exceeded` en ambos casos

#### Scenario: Envío que consume cupo
- **WHEN** se envía un enlace
- **THEN** el contador del periodo aumenta en uno

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

