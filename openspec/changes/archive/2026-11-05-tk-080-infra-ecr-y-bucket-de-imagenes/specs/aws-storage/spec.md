## ADDED Requirements

### Requirement: Registro privado de imágenes
Terraform SHALL crear los repositorios ECR `entrevecinos/api` y `entrevecinos/web` con etiquetas inmutables, escaneo al subir y una política de ciclo de vida que borre las imágenes sin etiqueta a los 7 días y conserve como mucho 10 etiquetadas.

#### Scenario: Etiqueta repetida
- **WHEN** se sube una imagen con una etiqueta que ya existe
- **THEN** ECR la rechaza

### Requirement: Bucket privado de fotografías
El bucket `entrevecinos-media-<cuenta>` SHALL bloquear todo acceso público, forzar el propietario de los objetos, cifrar con SSE-S3, denegar las peticiones sin TLS y versionar los objetos, conservando las versiones no actuales 30 días; MUST NOT tener CORS ni ninguna política que conceda acceso anónimo.

#### Scenario: Lectura sin firmar
- **WHEN** se pide un objeto del bucket sin URL prefirmada
- **THEN** la respuesta es `403`
