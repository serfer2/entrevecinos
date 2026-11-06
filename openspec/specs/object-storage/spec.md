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

### Requirement: Almacenamiento en S3 de AWS
`STORAGE_ENDPOINT`, `STORAGE_PUBLIC_ENDPOINT`, `STORAGE_ACCESS_KEY` y `STORAGE_SECRET_KEY` SHALL ser opcionales: sin endpoint se usa el de la región, sin endpoint público se firma con el de subida y sin claves se usan las credenciales de la cadena por defecto de AWS (rol de la instancia). `STORAGE_ACCESS_KEY` y `STORAGE_SECRET_KEY` MUST definirse las dos o ninguna. Las URL prefirmadas SHALL usar `STORAGE_REGION` (por defecto `us-east-1`) y `STORAGE_ADDRESSING_STYLE` (`path` por defecto, para MinIO, o `virtual`), que MUST rechazar otros valores.

#### Scenario: URL prefirmada en AWS
- **WHEN** la API firma una imagen sin claves, con `STORAGE_REGION=eu-north-1` y `STORAGE_ADDRESSING_STYLE=virtual`
- **THEN** la URL es `https://<bucket>.s3.eu-north-1.amazonaws.com/<clave>?…` y está firmada con las credenciales del rol

#### Scenario: Una sola clave
- **WHEN** se define `STORAGE_ACCESS_KEY` sin `STORAGE_SECRET_KEY`
- **THEN** la configuración falla con un error que nombra las dos variables

#### Scenario: MinIO sin cambios
- **WHEN** se usa el `.env` de desarrollo
- **THEN** las imágenes se suben a MinIO y se firman con `http://localhost:9000`

