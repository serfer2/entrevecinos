# web-email-verification Specification

## Purpose
Validación del correo desde el enlace (`/verificar-correo`) y su página de error.
## Requirements
### Requirement: Validación desde el enlace
La ruta pública `GET /verificar-correo?token=…` SHALL validar el token con la API y, con `200`, crear la sesión y redirigir a `/comunidades`. Con `410` MUST redirigir a `/verificar-correo/error?motivo=caducado&email=<correo>`; con `400`, a `/comunidades` si hay sesión y a `/iniciar-sesion?motivo=correo-validado` si no; sin token, a `motivo=invalido`; ante errores de red o `5xx`, a `motivo=error`. Las respuestas MUST llevar `Referrer-Policy: no-referrer` y `Cache-Control: no-store`.

#### Scenario: Enlace vigente
- **WHEN** el usuario abre el enlace del correo
- **THEN** llega a `/comunidades` con la sesión iniciada

#### Scenario: Enlace ya usado sin sesión
- **WHEN** abre de nuevo un enlace usado tras cerrar la sesión
- **THEN** llega a `/iniciar-sesion` con «Tu correo ya está validado. Inicia sesión.»

### Requirement: Página de error de la validación
La página pública `/verificar-correo/error` SHALL mostrar como alerta «El enlace de validación ha caducado.» (`caducado`), «El enlace de validación no es válido.» (`invalido` o motivo desconocido) o «No hemos podido validar tu correo. Inténtalo de nuevo más tarde.» (`error`), con un enlace al inicio de sesión.

#### Scenario: Enlace caducado
- **WHEN** el usuario abre un enlace caducado
- **THEN** ve «El enlace de validación ha caducado.» y sigue sin sesión
