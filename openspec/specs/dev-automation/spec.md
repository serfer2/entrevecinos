# dev-automation Specification

## Purpose
Comandos `make` de la raíz para construir, levantar y limpiar el entorno de desarrollo.
## Requirements
### Requirement: Construcción selectiva de imágenes
El Makefile SHALL ofrecer `build-frontend` (solo `web`), `build-backend` (solo `api`) y `build` (ambos, como prerequisitos de Make).

#### Scenario: build-frontend
- **WHEN** se ejecuta `make build-frontend` con `.env` presente
- **THEN** se construye solo la imagen `entrevecinos-web`

#### Scenario: build-backend
- **WHEN** se ejecuta `make build-backend` con `.env` presente
- **THEN** se construye solo la imagen `entrevecinos-api`

#### Scenario: build
- **WHEN** se ejecuta `make build`
- **THEN** quedan construidas `entrevecinos-web` y `entrevecinos-api`

### Requirement: Entorno de desarrollo completo
`make dev` SHALL construir las imágenes y levantar `db`, `mail`, `api` y `web` en segundo plano, y mostrar las URLs de la web, la API y el buzón de correo.

#### Scenario: dev
- **WHEN** se ejecuta `make dev` con los puertos por defecto
- **THEN** los servicios quedan en marcha y `http://localhost:3000`, `http://localhost:8000/docs` y `http://localhost:8025` responden

### Requirement: Limpieza sin pérdida de datos
`make clean` SHALL detener y eliminar los contenedores y las imágenes construidas localmente, y MUST NOT eliminar el volumen `db_data`.

#### Scenario: clean
- **WHEN** se ejecuta `make clean` con el entorno levantado
- **THEN** no quedan contenedores ni imágenes `entrevecinos-*`, y el volumen `entrevecinos_db_data` sigue existiendo

### Requirement: Ayuda y validación de entorno
`make` sin argumentos SHALL listar los targets con su descripción, y todo target que use Compose MUST fallar con un mensaje claro si falta `$(ENV_FILE)`.

#### Scenario: help por defecto
- **WHEN** se ejecuta `make`
- **THEN** se listan `build-frontend`, `build-backend`, `build`, `dev` y `clean` con su descripción

#### Scenario: Falta .env
- **WHEN** se ejecuta `make build` con `ENV_FILE=.env.noexiste`
- **THEN** el comando termina con error indicando que falta el fichero y que se copie `.env.example`

