## ADDED Requirements

### Requirement: Correo sin validar al iniciar sesión
Cuando la API responda `403` con `code: "email_not_verified"`, el formulario de inicio de sesión SHALL mostrar «Tienes que validar tu correo electrónico antes de iniciar sesión.» y conservar el correo. `/iniciar-sesion?motivo=correo-validado` SHALL mostrar el aviso «Tu correo ya está validado. Inicia sesión.».

#### Scenario: Cuenta sin validar
- **WHEN** una cuenta sin validar inicia sesión con la contraseña correcta
- **THEN** ve el mensaje de validación pendiente y no se crea la sesión
