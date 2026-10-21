## ADDED Requirements

### Requirement: Reenviar el correo de validación
El botón «Reenviar el correo de validación» SHALL aparecer en `/registro` cuando la API responda `409` con `code: "email_pending_verification"` (bajo el error «Este correo está pendiente de validación.»), en `/verificar-correo/error?motivo=caducado` con el `email` de la URL (sin él, solo un enlace a `/registro`) y en `/iniciar-sesion` tras el mensaje de correo sin validar. Mientras se envía muestra «Enviando…» y está deshabilitado; tras un `202` se sustituye por el aviso (`role="status"`) «Si tu cuenta está pendiente de validación, te hemos enviado un correo nuevo. Revisa tu bandeja de entrada.»; ante cualquier error muestra «No se pudo reenviar el correo. Inténtalo de nuevo.».

#### Scenario: Registro con un correo pendiente
- **WHEN** un visitante se registra con el correo de una cuenta pendiente
- **THEN** ve «Este correo está pendiente de validación.» y el botón de reenvío

#### Scenario: Correo no pendiente
- **WHEN** se pide el reenvío para un correo que no está pendiente
- **THEN** se muestra el mismo aviso de correo enviado
