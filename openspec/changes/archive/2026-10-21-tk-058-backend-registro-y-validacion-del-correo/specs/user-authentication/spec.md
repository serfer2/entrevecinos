## ADDED Requirements

### Requirement: Correo sin validar
Con la contraseña correcta, `POST /v1/auth/token` MUST responder `403` con `detail: "Tienes que validar tu correo electrónico antes de iniciar sesión."` y `code: "email_not_verified"` si la cuenta no ha validado su correo y no tiene rol `platform_admin`. Con la contraseña incorrecta, la respuesta SHALL seguir siendo el `401` genérico.

#### Scenario: Cuenta sin validar
- **WHEN** una cuenta `user` sin validar inicia sesión con su contraseña
- **THEN** la respuesta es `403` con `code: "email_not_verified"`

#### Scenario: Administrador de plataforma sin validar
- **WHEN** una cuenta `platform_admin` activa sin validar inicia sesión
- **THEN** la respuesta es `200`
