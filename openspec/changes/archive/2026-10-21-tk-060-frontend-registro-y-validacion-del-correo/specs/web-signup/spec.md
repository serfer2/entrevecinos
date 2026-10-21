## MODIFIED Requirements

### Requirement: Registro desde el navegador
La página `/registro` SHALL permitir crear una cuenta con nombre, correo, contraseña y teléfono opcional y, al terminar, sustituir el formulario por un aviso (`role="status"`): «Te hemos enviado un correo a {email}. Abre el enlace que contiene para activar tu cuenta. El enlace caduca en 24 horas.» y «Si no lo ves, revisa la carpeta de correo no deseado.». El registro MUST NOT crear la *cookie* `ev_session`.

#### Scenario: Registro correcto
- **WHEN** se envía el formulario con datos válidos y un correo no registrado
- **THEN** se muestra el aviso con el correo, no hay *cookie* `ev_session` y el usuario sigue en `/registro`
