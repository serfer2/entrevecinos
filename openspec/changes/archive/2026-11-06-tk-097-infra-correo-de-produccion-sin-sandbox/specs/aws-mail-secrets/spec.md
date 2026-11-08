## MODIFIED Requirements

### Requirement: Destinatarios de prueba en sandbox
Cada dirección de `ses_test_recipients` SHALL crearse como identidad de SES para poder recibir correo mientras la cuenta esté en *sandbox*. Con el correo de producción por Brevo (TK-098), la lista MUST estar vacía en producción, de modo que no queden identidades de prueba ni permiso de envío a ellas.

#### Scenario: Destinatario verificado
- **WHEN** el destinatario confirma el correo de verificación de AWS
- **THEN** su identidad queda verificada

#### Scenario: Producción con Brevo
- **WHEN** listo las identidades de SES de producción
- **THEN** solo queda `entrevecinos.org`
