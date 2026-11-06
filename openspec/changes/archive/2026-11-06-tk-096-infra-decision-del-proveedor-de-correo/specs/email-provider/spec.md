## ADDED Requirements

### Requirement: Proveedor de correo de producción
El correo de producción SHALL enviarse por SMTP con Brevo, con el dominio autenticado con el prefijo de marca `send`, y SES MUST seguir configurado como vuelta atrás. La decisión, su comparación por coste e integración, el estado real de SES y cómo volver MUST estar en `infra/aws/README.md`.

#### Scenario: Decisión documentada
- **WHEN** consulto «Decisiones de arquitectura» de `infra/aws/README.md`
- **THEN** encuentro por qué Brevo y no SES, el coste, los riesgos y cómo volver a SES

### Requirement: Credenciales SMTP fuera del repositorio
El usuario y la clave SMTP de Brevo SHALL guardarse solo en Parameter Store como `SecureString` (`/entrevecinos/prod/smtp/username` y `/entrevecinos/prod/smtp/password`) y MUST NOT aparecer en el repositorio, el estado de Terraform ni ficheros.

#### Scenario: Parámetros
- **WHEN** describo los parámetros de `/entrevecinos/prod/smtp/`
- **THEN** hay dos, de tipo `SecureString`
