# web-email-verification Specification

## Purpose
Validación del correo desde el enlace (`/verificar-correo`) y su página de error.
## Requirements
### Requirement: Validación desde el enlace
La ruta pública `GET /verificar-correo?token=…` SHALL validar el token con la API y, con `200`, crear la sesión y redirigir a `/comunidades`. Con `410` MUST redirigir a `/verificar-correo/error?motivo=caducado&email=<correo>`. Con `400` MUST decidir por el `code`: `email_already_verified`, a `/comunidades` si hay sesión y a `/iniciar-sesion?motivo=correo-validado` si no; `verification_superseded`, a `/verificar-correo/error?motivo=reemplazado&email=<correo>`; cualquier otro, a `motivo=invalido`. Sin token, a `motivo=invalido`; ante errores de red o `5xx`, a `motivo=error`. Las respuestas MUST llevar `Referrer-Policy: no-referrer` y `Cache-Control: no-store`.

#### Scenario: Enlace vigente
- **WHEN** el usuario abre el enlace del correo
- **THEN** llega a `/comunidades` con la sesión iniciada

#### Scenario: Enlace ya usado sin sesión
- **WHEN** abre de nuevo un enlace usado tras cerrar la sesión
- **THEN** llega a `/iniciar-sesion` con «Tu correo ya está validado. Inicia sesión.»

#### Scenario: Enlace sustituido sin sesión
- **WHEN** abre el enlace de un correo anterior a un reenvío y la cuenta sigue pendiente
- **THEN** llega a `/verificar-correo/error?motivo=reemplazado` y no se le dice que su correo está validado

#### Scenario: Enlace desconocido
- **WHEN** abre un enlace con un token inventado
- **THEN** ve «El enlace de validación no es válido.»

### Requirement: Página de error de la validación
La página pública `/verificar-correo/error` SHALL mostrar como alerta «El enlace de validación ha caducado.» (`caducado`), «Este enlace ya no es válido porque te hemos enviado uno más reciente. Abre el enlace del último correo que has recibido.» (`reemplazado`), «El enlace de validación no es válido.» (`invalido` o motivo desconocido) o «No hemos podido validar tu correo. Inténtalo de nuevo más tarde.» (`error`). Con `caducado` o `reemplazado` SHALL ofrecer el reenvío; con los demás motivos, un enlace al inicio de sesión. Siempre SHALL incluir el enlace «Volver al inicio» a `/`.

#### Scenario: Enlace caducado
- **WHEN** el usuario abre un enlace caducado
- **THEN** ve «El enlace de validación ha caducado.» y sigue sin sesión

#### Scenario: Enlace sustituido
- **WHEN** el usuario llega con `motivo=reemplazado` y su correo
- **THEN** ve el mensaje del enlace sustituido y el botón «Reenviar el correo de validación»

### Requirement: Reenviar el correo de validación
El botón «Reenviar el correo de validación» SHALL aparecer en `/registro` cuando la API responda `409` con `code: "email_pending_verification"` (bajo el error «Este correo está pendiente de validación.»), en `/verificar-correo/error` con `motivo=caducado` o `motivo=reemplazado` y el `email` de la URL (sin él, solo un enlace a `/registro`) y en `/iniciar-sesion` tras el mensaje de correo sin validar. Mientras se envía muestra «Enviando…» y está deshabilitado; tras un `202` se sustituye por el aviso (`role="status"`) «Si tu cuenta está pendiente de validación, te hemos enviado un correo nuevo. Revisa tu bandeja de entrada.»; ante cualquier error muestra «No se pudo reenviar el correo. Inténtalo de nuevo.».

#### Scenario: Registro con un correo pendiente
- **WHEN** un visitante se registra con el correo de una cuenta pendiente
- **THEN** ve «Este correo está pendiente de validación.» y el botón de reenvío

#### Scenario: Correo no pendiente
- **WHEN** se pide el reenvío para un correo que no está pendiente
- **THEN** se muestra el mismo aviso de correo enviado
