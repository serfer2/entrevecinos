## ADDED Requirements

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
