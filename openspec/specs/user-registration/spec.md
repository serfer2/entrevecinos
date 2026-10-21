# user-registration Specification

## Purpose
Registro de cuentas con correo y contraseña (`POST /v1/auth/register`), pendientes de validar el correo, y emisión del token de acceso JWT.
## Requirements
### Requirement: Registro de cuenta
`POST /v1/auth/register` SHALL crear una cuenta inactiva (`is_active = false`, `email_verified_at` nulo) con rol `user` a partir de `email`, `password`, `full_name` y `phone` opcional, enviar el correo de validación tras responder y responder `201` con `RegistrationResponse` (`email`, `verification_expires_at`). La respuesta MUST NOT incluir un token de acceso.

#### Scenario: Registro correcto
- **WHEN** se envía un correo no registrado, una contraseña de 12 a 128 caracteres y un nombre
- **THEN** la respuesta es `201` sin `access_token`, la cuenta queda inactiva, la contraseña se guarda como hash Argon2id y se envía un correo con el enlace `{WEB_PUBLIC_URL}/verificar-correo?token=…`

#### Scenario: Fallo del SMTP
- **WHEN** el servidor de correo no responde durante el registro
- **THEN** la respuesta sigue siendo `201`, la cuenta existe y el error queda en el log

### Requirement: Correo único sin distinguir mayúsculas
El registro MUST rechazar con `409` un correo ya registrado, comparando en minúsculas, sin crear ni modificar ninguna cuenta. Si la cuenta existente ha validado su correo (o es `platform_admin`), la respuesta SHALL ser `{"detail": "El correo ya está en uso.", "code": "email_in_use"}`; si está pendiente de validación, `{"detail": "Este correo está pendiente de validación.", "code": "email_pending_verification"}`.

#### Scenario: Correo repetido con otras mayúsculas
- **WHEN** existe la cuenta validada `vecino@example.com` y se registra `Vecino@Example.COM`
- **THEN** la respuesta es `409` con `code: "email_in_use"` y no se crea ninguna cuenta

#### Scenario: Correo pendiente de validación
- **WHEN** existe una cuenta pendiente con ese correo y se registra otra vez con otro nombre
- **THEN** la respuesta es `409` con `code: "email_pending_verification"`, la cuenta no cambia y no se envía ningún correo

### Requirement: Validación de datos
El registro MUST responder `422` con un error por campo (`loc`, `msg`, `type`) ante correo mal formado, nombre vacío o solo con espacios, contraseña fuera de 12–128 caracteres o campos no definidos en el contrato.

#### Scenario: Datos inválidos
- **WHEN** se envía un correo mal formado, un nombre `" "` y una contraseña corta
- **THEN** la respuesta es `422` con errores en `["body","email"]`, `["body","full_name"]` y `["body","password"]`

### Requirement: Errores sin datos sensibles
Las respuestas `422` MUST NOT incluir el campo `input` ni los valores enviados.

#### Scenario: Contraseña corta
- **WHEN** se envía una contraseña de menos de 12 caracteres
- **THEN** el cuerpo de la respuesta no contiene la contraseña ni `input`

### Requirement: Configuración del token
La API MUST negarse a arrancar sin `JWT_SECRET` (mínimo 32 caracteres); el token SHALL firmarse con HS256 y caducar a los `JWT_TTL_SECONDS` (por defecto 86400).

#### Scenario: Falta JWT_SECRET
- **WHEN** se crea la configuración sin `JWT_SECRET`
- **THEN** se lanza un error de validación que nombra `jwt_secret`

