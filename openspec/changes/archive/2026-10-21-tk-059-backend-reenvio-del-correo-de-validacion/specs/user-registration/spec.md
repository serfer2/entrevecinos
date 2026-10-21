## MODIFIED Requirements

### Requirement: Correo único sin distinguir mayúsculas
El registro MUST rechazar con `409` un correo ya registrado, comparando en minúsculas, sin crear ni modificar ninguna cuenta. Si la cuenta existente ha validado su correo (o es `platform_admin`), la respuesta SHALL ser `{"detail": "El correo ya está en uso.", "code": "email_in_use"}`; si está pendiente de validación, `{"detail": "Este correo está pendiente de validación.", "code": "email_pending_verification"}`.

#### Scenario: Correo repetido con otras mayúsculas
- **WHEN** existe la cuenta validada `vecino@example.com` y se registra `Vecino@Example.COM`
- **THEN** la respuesta es `409` con `code: "email_in_use"` y no se crea ninguna cuenta

#### Scenario: Correo pendiente de validación
- **WHEN** existe una cuenta pendiente con ese correo y se registra otra vez con otro nombre
- **THEN** la respuesta es `409` con `code: "email_pending_verification"`, la cuenta no cambia y no se envía ningún correo
