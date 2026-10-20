# listing-persistence Specification

## Purpose
Esquema de categorías, anuncios, ficheros de imagen e imágenes de anuncio.
## Requirements
### Requirement: Tablas de anuncios e imágenes
La migración `0004` SHALL crear los enums `listing_type` y `listing_status` y las tablas `category`, `listing`, `media_asset` y `listing_image`, con los índices recomendados por el modelo de datos, y cargar diez categorías iniciales.

#### Scenario: Categorías iniciales
- **WHEN** se aplica la migración
- **THEN** `category` contiene las diez categorías iniciales, activas, con `slug` válido

### Requirement: Coherencia del precio
La base de datos MUST rechazar un precio negativo, un precio sin moneda o una moneda sin precio, y SHALL aceptar un anuncio sin precio ni moneda.

#### Scenario: Precio sin moneda
- **WHEN** se inserta un anuncio con `price = 10` y `currency` nulo
- **THEN** falla la restricción `CHECK`

### Requirement: Imágenes de un anuncio
Un anuncio MUST tener como máximo una imagen de portada y no puede tener dos imágenes en la misma posición.

#### Scenario: Dos portadas
- **WHEN** se marca una segunda imagen como portada
- **THEN** la base de datos lo rechaza

### Requirement: Migración reversible
`alembic downgrade 0003` SHALL eliminar tablas, enums y la FK del avatar, y `upgrade head` volver a crearlos.

#### Scenario: Ida y vuelta
- **WHEN** se baja a `0003` y se sube a `head`
- **THEN** ambos terminan sin errores

