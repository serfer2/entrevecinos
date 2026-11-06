## MODIFIED Requirements

### Requirement: Registros de acceso
CloudFront SHALL enviar sus registros estándar de acceso (v2) a `/entrevecinos/prod/cloudfront` en `us-east-1`, con retención de 7 días, y MUST limitarse a los campos elegidos, sin `cs-uri-query`, `cs(Cookie)` ni `cs(Referer)`.

#### Scenario: Petición registrada
- **WHEN** pido una página de la web
- **THEN** la petición aparece en `/entrevecinos/prod/cloudfront` en unos minutos

#### Scenario: Sin cadena de consulta
- **WHEN** alguien abre `/verificar-correo?token=…`
- **THEN** su registro tiene `cs-uri-stem` `/verificar-correo` y ningún campo con el *token*
