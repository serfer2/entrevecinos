#!/bin/bash
# Roles de PostgreSQL de producción (TK-082). Idempotente: lo ejecuta la imagen oficial al crear
# la base (/docker-entrypoint-initdb.d) y deploy.sh en cada despliegue (TK-086), que así también
# aplica las contraseñas rotadas.
#
# - postgres: superusuario, solo para administración por Session Manager.
# - entrevecinos_owner: propietario de la base y del esquema; lo usan solo las migraciones.
# - entrevecinos_app: el de la API; solo lectura y escritura de datos, sin DDL.
#
# Las contraseñas llegan por entorno (nunca de ficheros): ENTREVECINOS_OWNER_PASSWORD y
# ENTREVECINOS_APP_PASSWORD.
set -euo pipefail

: "${ENTREVECINOS_OWNER_PASSWORD:?Falta ENTREVECINOS_OWNER_PASSWORD}"
: "${ENTREVECINOS_APP_PASSWORD:?Falta ENTREVECINOS_APP_PASSWORD}"
database="${POSTGRES_DB:-entrevecinos}"

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER:-postgres}" --dbname postgres \
  -v db="$database" \
  -v owner_password="$ENTREVECINOS_OWNER_PASSWORD" \
  -v app_password="$ENTREVECINOS_APP_PASSWORD" <<'SQL'
SELECT 'CREATE ROLE entrevecinos_owner LOGIN'
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'entrevecinos_owner') \gexec
SELECT 'CREATE ROLE entrevecinos_app LOGIN'
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'entrevecinos_app') \gexec
SELECT format('ALTER ROLE entrevecinos_owner PASSWORD %L', :'owner_password') \gexec
SELECT format('ALTER ROLE entrevecinos_app PASSWORD %L', :'app_password') \gexec

SELECT format('CREATE DATABASE %I OWNER entrevecinos_owner', :'db')
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = :'db') \gexec
SELECT format('ALTER DATABASE %I OWNER TO entrevecinos_owner', :'db') \gexec
SELECT format('REVOKE ALL ON DATABASE %I FROM PUBLIC', :'db') \gexec
SELECT format('GRANT CONNECT ON DATABASE %I TO entrevecinos_app', :'db') \gexec

\connect :db
ALTER SCHEMA public OWNER TO entrevecinos_owner;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO entrevecinos_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO entrevecinos_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO entrevecinos_app;
ALTER DEFAULT PRIVILEGES FOR ROLE entrevecinos_owner IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO entrevecinos_app;
ALTER DEFAULT PRIVILEGES FOR ROLE entrevecinos_owner IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO entrevecinos_app;
SQL
