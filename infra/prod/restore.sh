#!/bin/bash
# Restauración de PostgreSQL de producción desde una copia de backup.sh (TK-092). Se ejecuta como
# root en la instancia (Session Manager o Run Command):
#
#   restore.sh [--target <base>] <clave>        # ensayo: restaura en otra base (por defecto
#                                               # entrevecinos_restore) sin tocar producción
#   restore.sh --production --yes <clave>       # sustituye la base de producción
#   restore.sh --drop <base>                    # borra una base de ensayo o la anterior
#
# <clave> es la de la copia en el bucket: postgres/AAAA/MM/DD/AAAAMMDDTHHMMSSZ.dump.
#
# Siempre restaura en una base nueva como entrevecinos_owner y aplica los permisos de
# entrevecinos_app. En producción, además: copia previa de la base actual (backup.sh), API parada,
# cambio de nombre (entrevecinos → entrevecinos_anterior_<fecha>, la restaurada → entrevecinos) y
# API arrancada. La base anterior se conserva para volver atrás; se borra a mano.
#
# Las contraseñas se leen de Parameter Store y solo viven en el entorno de este proceso.
set -euo pipefail
set +x

readonly app_dir="${APP_DIR:-/opt/entrevecinos}"
readonly production_db=entrevecinos
readonly key_pattern='^postgres/[0-9]{4}/[0-9]{2}/[0-9]{2}/[0-9]{8}T[0-9]{6}Z\.dump$'
# Solo bases propias: nunca postgres ni las plantillas.
readonly db_pattern='^entrevecinos_[a-z0-9_]{1,50}$'
export AWS_REGION="${AWS_REGION:-eu-north-1}"

log() { echo "== $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }
usage() {
  fail "uso: restore.sh [--target <base>] <clave> | --production --yes <clave> | --drop <base>"
}

target=entrevecinos_restore production=false confirmed=false key="" drop=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) [[ $# -ge 2 ]] || usage; target="$2"; shift 2 ;;
    --drop) [[ $# -ge 2 ]] || usage; drop="$2"; shift 2 ;;
    --production) production=true; shift ;;
    --yes) confirmed=true; shift ;;
    -*) usage ;;
    *) [[ -z $key ]] || usage; key="$1"; shift ;;
  esac
done
if [[ -n $drop ]]; then
  [[ -z $key && $production == false ]] || usage
  target="$drop"
else
  [[ $key =~ $key_pattern ]] || fail "clave de copia no válida: ${key:-<vacía>}"
fi
[[ $target =~ $db_pattern ]] || fail "nombre de base no válido: $target"
[[ $target != "$production_db" ]] || fail "para sustituir producción, usa --production --yes"
if [[ $production == true && $confirmed != true ]]; then
  fail "--production sustituye la base de producción: repite la orden con --yes"
fi

container() {
  docker ps -q --filter "label=com.docker.compose.project=${COMPOSE_PROJECT:-entrevecinos}" \
    --filter "label=com.docker.compose.service=$1"
}
db_container="$(container db)"
[[ -n $db_container ]] || fail "el contenedor db no está en marcha"

postgres_password="" owner_password=""
while IFS=$'\t' read -r name value; do
  case "$name" in
    /entrevecinos/prod/db/postgres-password) postgres_password="$value" ;;
    /entrevecinos/prod/db/owner-password) owner_password="$value" ;;
  esac
done < <(aws ssm get-parameters --with-decryption --output text --query 'Parameters[].[Name,Value]' \
  --names /entrevecinos/prod/db/postgres-password /entrevecinos/prod/db/owner-password)
[[ -n $postgres_password && -n $owner_password ]] || fail "faltan contraseñas en Parameter Store"

# psql o pg_restore en el contenedor db, con la contraseña solo en su entorno.
as_postgres() { PGPASSWORD="$postgres_password" docker exec -i -e PGPASSWORD "$db_container" "$@" --username=postgres; }
as_owner() { PGPASSWORD="$owner_password" docker exec -i -e PGPASSWORD "$db_container" "$@" --username=entrevecinos_owner; }
sql() { as_postgres psql -v ON_ERROR_STOP=1 -qAt "$@"; }

if [[ -n $drop ]]; then
  log "Borrado de la base $drop"
  sql --dbname=postgres -v db="$drop" <<<"SELECT format('DROP DATABASE IF EXISTS %I WITH (FORCE)', :'db') \gexec"
  exit 0
fi

# shellcheck source=/dev/null # BACKUP_BUCKET, lo escribe deploy.sh
source "$app_dir/backup.env"
: "${BACKUP_BUCKET:?Falta BACKUP_BUCKET en $app_dir/backup.env}"
readonly uri="s3://${BACKUP_BUCKET}/${key}"

aws s3api head-object --bucket "$BACKUP_BUCKET" --key "$key" >/dev/null ||
  fail "no existe la copia $uri"

started=$SECONDS

if [[ $production == true ]]; then
  log "Copia previa de la base actual"
  systemctl start entrevecinos-backup.service
fi

log "Base $target desde $uri"
sql --dbname=postgres -v db="$target" <<'SQL'
SELECT format('DROP DATABASE IF EXISTS %I WITH (FORCE)', :'db') \gexec
SELECT format('CREATE DATABASE %I OWNER entrevecinos_owner', :'db') \gexec
SELECT format('REVOKE ALL ON DATABASE %I FROM PUBLIC', :'db') \gexec
SELECT format('GRANT CONNECT ON DATABASE %I TO entrevecinos_app', :'db') \gexec
SQL
aws s3 cp "$uri" - --only-show-errors |
  as_owner pg_restore --no-owner --exit-on-error --dbname="$target"

log "Permisos de entrevecinos_app"
sql --dbname="$target" <<'SQL'
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

counts="SELECT 'users', count(*) FROM users UNION ALL SELECT 'community', count(*) FROM community
  UNION ALL SELECT 'listing', count(*) FROM listing UNION ALL SELECT 'media_asset', count(*) FROM media_asset"
log "Contenido de $target (restaurada)"
sql --dbname="$target" -F ' ' -c "$counts"
log "Contenido de $production_db (actual, para comparar)"
sql --dbname="$production_db" -F ' ' -c "$counts"

if [[ $production == true ]]; then
  previous="${production_db}_anterior_$(date -u +%Y%m%dT%H%M%SZ)"
  api_container="$(container api)"
  restart_api() { [[ -z $api_container ]] || docker start "$api_container" >/dev/null; }
  trap restart_api EXIT

  log "API parada; $production_db → $previous, $target → $production_db"
  [[ -z $api_container ]] || docker stop "$api_container" >/dev/null
  sql --dbname=postgres -v prod="$production_db" -v prev="$previous" -v new="$target" <<'SQL'
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE datname IN (:'prod', :'new') AND pid <> pg_backend_pid();
SELECT format('ALTER DATABASE %I RENAME TO %I', :'prod', :'prev') \gexec
SELECT format('ALTER DATABASE %I RENAME TO %I', :'new', :'prod') \gexec
SQL
  log "API arrancada"
  restart_api
  trap - EXIT
  echo "Base anterior conservada: $previous"
  echo "Bórrala cuando compruebes la restauración: DROP DATABASE $previous;"
fi

echo "Restauración correcta en $((SECONDS - started)) s"
