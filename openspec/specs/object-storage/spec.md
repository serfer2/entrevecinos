# object-storage Specification

## Purpose
Almacenamiento de objetos local (MinIO) para las imágenes: bucket privado y credenciales mínimas de la API.
## Requirements
### Requirement: Servicio de almacenamiento local
`make dev` SHALL levantar `storage` (MinIO con versión fija) y ejecutar `storage-init` antes de `api`; el volumen `storage_data` MUST conservar los objetos entre recreaciones de los contenedores.

#### Scenario: Arranque
- **WHEN** se ejecuta `make dev` con un `.env` copiado de `.env.example`
- **THEN** `storage` queda `healthy`, `storage-init` termina con código 0 y `api` arranca después

### Requirement: Bucket privado y credenciales mínimas
El bucket MUST ser privado y la API SHALL usar un usuario propio que solo puede leer, escribir y borrar objetos de ese bucket.

#### Scenario: Lectura anónima
- **WHEN** se pide un objeto sin firma
- **THEN** la respuesta es `403`

#### Scenario: Credenciales de la API
- **WHEN** se usan las credenciales de la API
- **THEN** puede subir y leer objetos del bucket, pero no listar los buckets

### Requirement: Exposición mínima
Solo la API S3 SHALL publicarse, en `127.0.0.1`; la consola MUST quedar sin publicar salvo con el *override* de depuración.

#### Scenario: Puertos
- **WHEN** se revisan los puertos de `storage`
- **THEN** solo aparece `127.0.0.1:9000`

