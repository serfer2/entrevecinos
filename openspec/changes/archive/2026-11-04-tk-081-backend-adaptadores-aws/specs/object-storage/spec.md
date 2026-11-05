## ADDED Requirements

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
