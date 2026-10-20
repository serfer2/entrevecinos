# TK-001 · Infraestructura: Docker Compose con PostgreSQL 16

| Campo | Valor |
|---|---|
| **Tipo** | Infraestructura / DevOps |
| **Componente** | `infra/` |
| **Prioridad** | Alta (bloquea TK-002 y TK-003) |
| **Depende de** | — |
| **Referencias** | `readme.md` §2.1 (arquitectura), §2.3 (estructura de ficheros), §2.4 (desarrollo local), §2.5 (seguridad) |

Las inferencias que no aparecen explícitamente en el README se marcan con `(asumido)`.

## 1. Contexto y objetivo

El README define que el entorno local se levanta con Docker Compose y que PostgreSQL 16 se ejecuta en un contenedor con volumen persistente, dentro de una red interna y sin exponerse a Internet. El repositorio aún no contiene ninguna configuración de Docker.

**Objetivo:** crear la base de la configuración de Docker Compose del proyecto con un primer servicio, `db` (PostgreSQL 16), con datos persistentes, credenciales fuera del repositorio y comprobación de salud, de forma que TK-002 y TK-003 puedan añadir sus servicios sobre esta base.

## 2. Alcance

**Incluye**
- Fichero `infra/docker-compose.yml` con el servicio `db`, un volumen con nombre y las redes.
- Fichero `.env.example` con las variables de la base de datos y `.env` excluido del repositorio.
- Carpeta `infra/postgres/` con el espacio previsto en el README para inicialización y configuración.
- Ajustes de `.gitignore` necesarios.
- Documentación breve de uso en `infra/README.md`.

**No incluye**
- Esquema, tablas, enums, migraciones ni datos semilla (tickets posteriores de base de datos).
- Servicios `api` y `web` (TK-002 y TK-003).
- Almacenamiento de imágenes, copias de seguridad automáticas y configuración de producción.

## 3. Requisitos técnicos

### 3.1 Servicio `db`

- **Imagen:** `postgres:16` (Debian) (asumido: se prefiere a la variante Alpine porque el modelo de datos prevé búsqueda de texto completo y la variante glibc evita diferencias de *collation* respecto a producción). Fijar solo la versión mayor en local; fijar la menor en el ticket de producción.
- **Volumen persistente:** volumen con nombre `db_data` montado en `/var/lib/postgresql/data`. No usar *bind mounts* a carpetas del repositorio para los datos.
- **Credenciales:** `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB` se leen del entorno. `POSTGRES_PASSWORD` es obligatoria: si falta, Compose debe fallar con un mensaje claro (`${POSTGRES_PASSWORD:?...}`).
- **Zona horaria:** `TZ=UTC` y `PGTZ=UTC` (asumido: el modelo usa `TIMESTAMPTZ`).
- **Healthcheck:** `pg_isready -U $POSTGRES_USER -d $POSTGRES_DB` con intervalo, *timeout*, reintentos y `start_period` explícitos. Los servicios que dependan de `db` usarán `depends_on: condition: service_healthy`.
- **Reinicio:** `restart: unless-stopped`.
- **Inicialización:** montar `infra/postgres/initdb/` en `/docker-entrypoint-initdb.d/` en modo solo lectura. Esos scripts solo se ejecutan cuando el volumen está vacío; documentarlo. La carpeta se entrega vacía (con `.gitkeep`).

### 3.2 Redes

- `data`: red interna (`internal: true`) para `db` y, más adelante, `api`. Impide que la base de datos sea accesible desde fuera de Docker.
- `edge`: red normal donde se conectarán `web` y `api` (se usa en TK-002 y TK-003; se declara ya para no reescribir el fichero).

### 3.3 Acceso desde el host

- Por defecto, `db` **no publica puertos**, en línea con §2.5 del README.
- Para depurar con un cliente local se ofrece un mecanismo opcional (asumido): un fichero `infra/docker-compose.db-debug.yml` que publica `127.0.0.1:${POSTGRES_HOST_PORT:-5432}:5432`. Nunca se publica en `0.0.0.0`.

### 3.4 Variables de entorno (`.env.example`, valores ficticios)

```dotenv
# --- PostgreSQL ---
POSTGRES_USER=entrevecinos
POSTGRES_PASSWORD=change-me
POSTGRES_DB=entrevecinos
POSTGRES_HOST_PORT=5432   # solo para docker-compose.db-debug.yml
```

`.env` real: excluido en `.gitignore`. Docker Compose lo lee desde la raíz del repositorio (`--env-file .env` al usar `-f infra/docker-compose.yml`).

### 3.5 Referencia de `infra/docker-compose.yml`

```yaml
name: entrevecinos

services:
  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-entrevecinos}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Define POSTGRES_PASSWORD en .env}
      POSTGRES_DB: ${POSTGRES_DB:-entrevecinos}
      TZ: UTC
      PGTZ: UTC
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./postgres/initdb:/docker-entrypoint-initdb.d:ro
    networks:
      - data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

volumes:
  db_data:

networks:
  data:
    internal: true
  edge:
```

### 3.6 Ficheros a crear o modificar

```
.env.example
.gitignore                         # añadir: .env
infra/
├── README.md                      # cómo levantar, parar, borrar datos, depurar
├── docker-compose.yml
├── docker-compose.db-debug.yml    # publicación opcional en 127.0.0.1
└── postgres/
    └── initdb/.gitkeep
```

## 4. Criterios de aceptación

**AC1 — Arranque con base de datos sana**

- **Given** un `.env` creado a partir de `.env.example` y Docker instalado
- **When** ejecuto `docker compose --env-file .env -f infra/docker-compose.yml up -d db`
- **Then** el contenedor `db` alcanza el estado `healthy` y acepta conexiones con las credenciales del `.env`

**AC2 — Persistencia de datos**

- **Given** que `db` está en marcha y he creado una tabla de prueba con un registro
- **When** ejecuto `down` (sin `-v`) y vuelvo a ejecutar `up -d db`
- **Then** la tabla y el registro siguen existiendo

**AC3 — Contraseña obligatoria**

- **Given** que no existe `.env` o no define `POSTGRES_PASSWORD`
- **When** ejecuto `docker compose -f infra/docker-compose.yml config`
- **Then** el comando falla con el mensaje que pide definir `POSTGRES_PASSWORD`

**AC4 — Base de datos no expuesta**

- **Given** que `db` está en marcha con la configuración por defecto
- **When** intento conectarme a `localhost:5432` desde el host
- **Then** la conexión es rechazada porque el puerto no está publicado

**AC5 — Secretos fuera del repositorio**

- **Given** un `.env` local con credenciales
- **When** ejecuto `git status`
- **Then** `.env` no aparece como fichero a añadir y `.env.example` solo contiene valores ficticios

## 5. Plan de tareas

1. Crear la estructura `infra/` y `infra/postgres/initdb/`.
2. Escribir `infra/docker-compose.yml` con `db`, `db_data`, redes `data` y `edge`.
3. Escribir `.env.example` y actualizar `.gitignore`.
4. Crear `infra/docker-compose.db-debug.yml`.
5. Redactar `infra/README.md` (comandos, advertencia sobre `initdb`, cómo borrar el volumen con `down -v`).
6. Validar con la lista de verificación de la sección 6.

## 6. Verificación

```bash
cp .env.example .env
docker compose --env-file .env -f infra/docker-compose.yml config          # sintaxis y variables
docker compose --env-file .env -f infra/docker-compose.yml up -d db
docker compose --env-file .env -f infra/docker-compose.yml ps               # estado healthy
docker compose --env-file .env -f infra/docker-compose.yml exec db \
  psql -U entrevecinos -d entrevecinos -c "select version();"               # PostgreSQL 16.x
docker compose --env-file .env -f infra/docker-compose.yml exec db \
  psql -U entrevecinos -c "create table t(id int); insert into t values (1);"
docker compose --env-file .env -f infra/docker-compose.yml down
docker compose --env-file .env -f infra/docker-compose.yml up -d db
docker compose --env-file .env -f infra/docker-compose.yml exec db \
  psql -U entrevecinos -c "select * from t;"                                # el dato persiste
docker compose --env-file .env -f infra/docker-compose.yml down -v          # limpieza
```

## 7. Definición de terminado

- [ ] Los cinco criterios de aceptación se cumplen.
- [ ] `docker compose config` no emite advertencias.
- [ ] No hay credenciales reales en el repositorio.
- [ ] `infra/README.md` permite a otra persona levantar la base de datos sin ayuda.
- [ ] Cambios revisados y fusionados mediante pull request.

## 8. Riesgos y decisiones abiertas

- **Conflicto de puerto 5432:** por eso no se publica por defecto y el puerto del host es configurable.
- **Scripts de `initdb` no se reejecutan** si el volumen ya existe; documentado en `infra/README.md`.
- **Copias de seguridad de `db_data`:** el README las exige en producción; quedan fuera de este ticket.
