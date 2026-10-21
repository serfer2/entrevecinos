## ADDED Requirements

### Requirement: Reenviar el enlace de validación
`POST /v1/auth/email-verification/resend` (público, cuerpo `{"email": "..."}` sin campos adicionales) SHALL responder siempre `202` con `{"detail": "Si el correo está pendiente de validación, te enviaremos un enlace nuevo."}`. Solo si el correo pertenece a una cuenta pendiente de validación y su último enlace tiene al menos 60 segundos (o no tiene ninguno), SHALL crear un enlace nuevo con caducidad de 24 horas, que sustituye a los anteriores, y enviarlo tras responder.

#### Scenario: Cuenta pendiente
- **WHEN** se pide el reenvío para una cuenta pendiente cuyo último enlace tiene más de 60 segundos
- **THEN** la respuesta es `202`, llega un correo nuevo válido 24 horas y el enlace anterior responde `400`

#### Scenario: Sin revelar cuentas
- **WHEN** se pide el reenvío para un correo inexistente, una cuenta validada o antes de 60 segundos
- **THEN** la respuesta es el mismo `202` y no se envía ningún correo
