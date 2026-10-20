## 1. Infraestructura

- [x] 1.1 Dependencias `boto3` y `python-multipart`; `Settings` de almacenamiento y medios
- [x] 1.2 `S3ObjectStorage` (subida interna, firma pública)

## 2. Dominio y aplicación

- [x] 2.1 `domain/media` (`ImageType`, `detect_image_type`, errores) con pruebas
- [x] 2.2 `UploadImage` y `GetImageUrl` con puertos y pruebas unitarias

## 3. Persistencia y presentación

- [x] 3.1 `SqlAlchemyMediaRepository` con la regla de lectura
- [x] 3.2 `POST /v1/media` (límites 413/415/422) y `GET /v1/media/{id}` (302)

## 4. Pruebas y verificación

- [x] 4.1 Integración (subida, formatos, tamaño, lectura) y prueba `storage` contra MinIO real
- [x] 4.2 Verificación TK-021 §6
