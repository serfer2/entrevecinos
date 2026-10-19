## ADDED Requirements

### Requirement: Registro de cuenta
`POST /v1/auth/register` SHALL crear una cuenta con rol `user` a partir de `email`, `password`, `full_name` y `phone` opcional, y responder `201` con `AuthResponse` (`access_token`, `token_type: "Bearer"`, `expires_in`, `user`).

#### Scenario: Registro correcto
- **WHEN** se envía un correo no registrado, una contraseña de 12 a 128 caracteres y un nombre
- **THEN** la respuesta es `201`, el `sub` del token es el `id` del usuario y la contraseña se guarda como hash Argon2id

### Requirement: Correo único sin distinguir mayúsculas
El registro MUST rechazar con `409` y `detail: "El correo ya está en uso."` un correo ya registrado, comparando en minúsculas.

#### Scenario: Correo repetido con otras mayúsculas
- **WHEN** existe `vecino@example.com` y se registra `Vecino@Example.COM`
- **THEN** la respuesta es `409` y no se crea ninguna cuenta

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
