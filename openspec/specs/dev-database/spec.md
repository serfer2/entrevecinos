# dev-database Specification

## Purpose
Base de datos PostgreSQL 16 del entorno local de desarrollo (servicio `db` de `infra/docker-compose.yml`).
## Requirements
### Requirement: Arranque de la base de datos sana
El entorno local SHALL definir un servicio `db` basado en `postgres:16` en `infra/docker-compose.yml` que alcance el estado `healthy` mediante `pg_isready` y acepte conexiones con las credenciales definidas en `.env`.

#### Scenario: Arranque con .env válido
- **WHEN** existe un `.env` copiado de `.env.example` y se ejecuta `docker compose --env-file .env -f infra/docker-compose.yml up -d db`
- **THEN** el contenedor `db` queda `healthy` y `psql` con el usuario y la base de datos del `.env` devuelve una versión 16.x

### Requirement: Persistencia de datos
Los datos de PostgreSQL SHALL guardarse en el volumen con nombre `db_data` y sobrevivir a la recreación de los contenedores sin `-v`.

#### Scenario: Datos tras down y up
- **WHEN** se crea una tabla con un registro, se ejecuta `down` sin `-v` y después `up -d db`
- **THEN** la tabla y el registro siguen existiendo

### Requirement: Contraseña obligatoria
La configuración de Compose MUST fallar con un mensaje que pida definir `POSTGRES_PASSWORD` cuando esa variable no esté definida.

#### Scenario: Falta POSTGRES_PASSWORD
- **WHEN** se ejecuta `docker compose -f infra/docker-compose.yml config` sin `.env` o sin `POSTGRES_PASSWORD`
- **THEN** el comando termina con error y el mensaje pide definir `POSTGRES_PASSWORD`

### Requirement: Base de datos no expuesta por defecto
Con la configuración por defecto, el servicio `db` MUST NOT publicar puertos en el host y SHALL estar solo en la red interna `data`.

#### Scenario: Conexión desde el host
- **WHEN** `db` está en marcha con solo `infra/docker-compose.yml` y se intenta conectar a `localhost:5432` desde el host
- **THEN** la conexión es rechazada

### Requirement: Acceso de depuración opcional
El override `infra/docker-compose.db-debug.yml` SHALL publicar el puerto de PostgreSQL únicamente en `127.0.0.1:${POSTGRES_HOST_PORT:-5432}`.

#### Scenario: Override de depuración activo
- **WHEN** se levanta `db` añadiendo `-f infra/docker-compose.db-debug.yml`
- **THEN** el puerto se publica en `127.0.0.1` y nunca en `0.0.0.0`

### Requirement: Secretos fuera del repositorio
El fichero `.env` MUST estar excluido por `.gitignore` y `.env.example` SHALL contener solo valores ficticios.

#### Scenario: git status con .env local
- **WHEN** existe un `.env` local con credenciales y se ejecuta `git status`
- **THEN** `.env` no aparece como fichero sin seguimiento

