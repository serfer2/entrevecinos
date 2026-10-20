# media-upload Specification

## Purpose
Subida de imágenes al almacenamiento de objetos y lectura con permisos mediante URL prefirmadas.
## Requirements
### Requirement: Subir una imagen
`POST /v1/media` (multipart, campo `file`) SHALL guardar una imagen JPEG, PNG o WebP de hasta 5 MB en el almacenamiento de objetos con una clave que no contiene el nombre original, y responder `201` con `MediaAsset` (`url: "/v1/media/<id>"`).

#### Scenario: JPEG
- **WHEN** un usuario autenticado sube un JPEG de 1 MB
- **THEN** recibe `201` con `mime_type: "image/jpeg"` y el objeto existe en el bucket

### Requirement: Tipo y tamaño
El tipo MUST decidirse por los *magic bytes*, ignorando el `Content-Type` y la extensión: otro formato SHALL responder `415`, más de 5 MB `413` y un fichero vacío `422`, sin guardar nada.

#### Scenario: PDF renombrado
- **WHEN** se sube un PDF con nombre `foto.jpg` y `Content-Type: image/jpeg`
- **THEN** la respuesta es `415 {"detail": "Formato no permitido. Usa JPEG, PNG o WebP."}`

#### Scenario: Demasiado grande
- **WHEN** se sube una imagen de 5 MB + 1 byte
- **THEN** la respuesta es `413 {"detail": "La imagen supera el tamaño máximo de 5 MB."}`

### Requirement: Leer una imagen
`GET /v1/media/{asset_id}` SHALL responder `302` a una URL prefirmada del host público (válida 300 s) a quien la subió o a un miembro aprobado de la comunidad de un anuncio visible que la use; a cualquier otro usuario MUST responder `403`, y `404` si no existe.

#### Scenario: Miembro de la comunidad
- **WHEN** un miembro aprobado pide una imagen de un anuncio de su comunidad
- **THEN** recibe `302` con `Location` en `http://localhost:9000/…`

#### Scenario: Ajeno
- **WHEN** un usuario de otra comunidad la pide
- **THEN** recibe `403`

