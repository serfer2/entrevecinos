## ADDED Requirements

### Requirement: Configuración de envío de SES
Terraform SHALL crear el *configuration set* `entrevecinos-prod` con TLS obligatorio, métricas de reputación y supresión de rebotes y quejas, que MUST publicar en CloudWatch los eventos `SEND`, `REJECT`, `BOUNCE`, `COMPLAINT` y `DELIVERY`, y la lista de supresión de la cuenta MUST incluir rebotes y quejas.

#### Scenario: Eventos de envío
- **WHEN** consulto los destinos de eventos del *configuration set*
- **THEN** hay un destino de CloudWatch activo con esos cinco tipos de evento

### Requirement: Destinatarios de prueba en sandbox
Cada dirección de `ses_test_recipients` SHALL crearse como identidad de SES para poder recibir correo mientras la cuenta esté en *sandbox*.

#### Scenario: Destinatario verificado
- **WHEN** el destinatario confirma el correo de verificación de AWS
- **THEN** su identidad queda verificada

### Requirement: Secreto de los JWT fuera del repositorio y del estado
El secreto de los JWT SHALL guardarse como `SecureString` en `/entrevecinos/prod/jwt-secret`, generado en Terraform con un recurso efímero y escrito con un argumento de solo escritura, y MUST NOT aparecer en el repositorio ni en el estado de Terraform.

#### Scenario: Estado sin secreto
- **WHEN** busco el valor del secreto en el estado de Terraform
- **THEN** no aparece; solo `value_wo_version`
