## MODIFIED Requirements

### Requirement: Registro desde el navegador
La página `/registro` SHALL permitir crear una cuenta con nombre, correo, contraseña y teléfono opcional y, al terminar, redirigir a `/comunidades` con la *cookie* `ev_session` (`HttpOnly`, `SameSite=Lax`).

#### Scenario: Registro correcto
- **WHEN** se envía el formulario con datos válidos y un correo no registrado
- **THEN** el navegador queda en `/comunidades` y la *cookie* `ev_session` no es accesible desde `document.cookie`
