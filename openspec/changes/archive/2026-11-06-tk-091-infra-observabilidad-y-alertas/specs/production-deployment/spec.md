## MODIFIED Requirements

### Requirement: Logs en CloudWatch
Los contenedores SHALL enviar sus logs con el *driver* `awslogs` a `/entrevecinos/prod/app/<servicio>`, con retención de 14 días; la salida de cada despliegue MUST quedar en `/entrevecinos/prod/app/deploy` (30 días) y la de las copias en `/entrevecinos/prod/app/backup` (14 días). El proxy MUST registrar el método, la ruta sin la cadena de consulta y el protocolo, nunca la petición completa.

#### Scenario: Logs de la API
- **WHEN** la API atiende peticiones
- **THEN** sus logs aparecen en `/entrevecinos/prod/app/api`

#### Scenario: Proxy sin cadena de consulta
- **WHEN** alguien abre `/verificar-correo?token=…`
- **THEN** el registro del proxy muestra `GET /verificar-correo HTTP/1.1`
