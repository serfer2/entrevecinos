#!/bin/bash
# Despliegue de producción (TK-086). Lo ejecuta como root el documento de SSM entrevecinos-deploy,
# que antes copia a /opt/entrevecinos el Compose y infra/prod/:
#
#   deploy.sh <digest de api> <digest de web>      # sha256:<64 hex>
#
# 1. Credenciales de ECR con el rol de la instancia (credential helper: ningún token en disco).
# 2. Secretos de Parameter Store solo al entorno de este proceso: ni .env ni ficheros temporales.
# 3. PostgreSQL en marcha y roles al día (aplica también las contraseñas rotadas).
# 4. Migraciones como entrevecinos_owner.
# 5. Servicios nuevos, healthy y respondiendo por el proxy; si no, vuelta a los digests anteriores
#    (sin deshacer migraciones) y error.
# 6. Digests guardados, temporizador de copias instalado e imágenes antiguas eliminadas.
#
# Nunca imprime secretos: sin traza y sin `docker compose config`.
set -euo pipefail
set +x

readonly app_dir=/opt/entrevecinos
readonly compose_file="$app_dir/docker-compose.prod.yml"
readonly digests_file="$app_dir/current-digests"
readonly registry=995006761619.dkr.ecr.eu-north-1.amazonaws.com
readonly digest_pattern='^sha256:[a-f0-9]{64}$'
readonly wait_timeout="${WAIT_TIMEOUT:-240}"
readonly secret_vars=(JWT_SECRET POSTGRES_PASSWORD ENTREVECINOS_OWNER_PASSWORD
  ENTREVECINOS_APP_PASSWORD ORIGIN_VERIFY DATABASE_URL)

export AWS_REGION=eu-north-1
# El agente de SSM no siempre define HOME: la configuración de Docker, siempre la de root.
export DOCKER_CONFIG=/root/.docker

log() { echo "== $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }
compose() { docker compose -f "$compose_file" "$@"; }

discard_secrets() { unset "${secret_vars[@]}"; }
trap discard_secrets EXIT

[[ $# -eq 2 ]] || fail "uso: deploy.sh <digest de api> <digest de web>"
[[ $1 =~ $digest_pattern && $2 =~ $digest_pattern ]] || fail "digests no válidos"
readonly new_api="$1" new_web="$2"

configure_ecr() {
  command -v docker-credential-ecr-login >/dev/null ||
    dnf -y -q install amazon-ecr-credential-helper
  install -d -m 700 "$DOCKER_CONFIG"
  printf '{"credHelpers":{"%s":"ecr-login"}}\n' "$registry" >"$DOCKER_CONFIG/config.json"
}

load_secrets() {
  local name value
  # Se exportan a docker compose, que los interpola en el Compose (${VAR:?}).
  export JWT_SECRET ORIGIN_VERIFY POSTGRES_PASSWORD ENTREVECINOS_OWNER_PASSWORD \
    ENTREVECINOS_APP_PASSWORD
  # Una sola llamada; los valores llegan por una tubería y solo quedan en variables.
  while IFS=$'\t' read -r name value; do
    case "$name" in
      /entrevecinos/prod/jwt-secret) JWT_SECRET="$value" ;;
      /entrevecinos/prod/origin-verify) ORIGIN_VERIFY="$value" ;;
      /entrevecinos/prod/db/postgres-password) POSTGRES_PASSWORD="$value" ;;
      /entrevecinos/prod/db/owner-password) ENTREVECINOS_OWNER_PASSWORD="$value" ;;
      /entrevecinos/prod/db/app-password) ENTREVECINOS_APP_PASSWORD="$value" ;;
    esac
  done < <(aws ssm get-parameters --with-decryption --output text \
    --query 'Parameters[].[Name,Value]' --names \
    /entrevecinos/prod/jwt-secret /entrevecinos/prod/origin-verify \
    /entrevecinos/prod/db/postgres-password /entrevecinos/prod/db/owner-password \
    /entrevecinos/prod/db/app-password)

  local var
  for var in JWT_SECRET ORIGIN_VERIFY POSTGRES_PASSWORD ENTREVECINOS_OWNER_PASSWORD \
    ENTREVECINOS_APP_PASSWORD; do
    [[ -n ${!var:-} ]] || fail "falta el parámetro de $var en Parameter Store"
  done
}

use_images() {
  export API_IMAGE="$registry/entrevecinos/api@$1"
  export WEB_IMAGE="$registry/entrevecinos/web@$2"
}

# La web responde a través del proxy con la cabecera de origen (por la entrada estándar de curl,
# para que no aparezca en la lista de procesos).
check_origin() {
  printf 'X-Origin-Verify: %s\n' "$ORIGIN_VERIFY" |
    curl -fsS -o /dev/null --max-time 10 --retry 5 --retry-delay 3 --retry-all-errors \
      -H @- http://127.0.0.1/
}

start_services() {
  compose up -d --remove-orphans --wait --wait-timeout "$wait_timeout" && check_origin
}

previous_digests() {
  [[ -f $digests_file ]] || return 1
  local api web
  api="$(sed -n 's/^API_DIGEST=//p' "$digests_file")"
  web="$(sed -n 's/^WEB_DIGEST=//p' "$digests_file")"
  [[ $api =~ $digest_pattern && $web =~ $digest_pattern ]] || return 1
  echo "$api $web"
}

rollback() {
  local previous
  if ! previous="$(previous_digests)"; then
    fail "el despliegue ha fallado y no hay digests anteriores a los que volver"
  fi
  # shellcheck disable=SC2086 # dos palabras: digest de api y de web
  set -- $previous
  log "Vuelta atrás: api $1, web $2"
  use_images "$1" "$2"
  start_services || fail "la vuelta atrás también ha fallado"
  fail "el despliegue ha fallado; se han restaurado los digests anteriores"
}

install_backups() {
  # Configuración no secreta de backup.sh; la contraseña la lee el propio script.
  printf 'BACKUP_BUCKET=entrevecinos-backups-995006761619\nAWS_REGION=%s\n' "$AWS_REGION" \
    >"$app_dir/backup.env"
  install -m 644 "$app_dir"/prod/systemd/entrevecinos-backup.{service,timer} /etc/systemd/system/
  systemctl daemon-reload
  systemctl enable --now entrevecinos-backup.timer
}

log "Despliegue: api $new_api, web $new_web"
configure_ecr
load_secrets
use_images "$new_api" "$new_web"

log "Descarga de imágenes"
compose pull --quiet

log "PostgreSQL y roles"
compose up -d --wait --wait-timeout "$wait_timeout" db
compose exec -T db bash /docker-entrypoint-initdb.d/10-roles.sh

log "Migraciones"
DATABASE_URL="postgresql+psycopg://entrevecinos_owner:${ENTREVECINOS_OWNER_PASSWORD}@db:5432/entrevecinos"
export DATABASE_URL
compose run --rm --no-deps -T -e DATABASE_URL api alembic upgrade head
unset DATABASE_URL

log "Servicios"
start_services || rollback

printf 'API_DIGEST=%s\nWEB_DIGEST=%s\n' "$new_api" "$new_web" >"$digests_file"

log "Copias de PostgreSQL"
install_backups

log "Limpieza de imágenes sin uso"
docker image prune -af >/dev/null

log "Despliegue correcto"
