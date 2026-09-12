#!/bin/sh
set -eu

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-new-api-test}"
STANDARD_DEPLOY_DIR="${STANDARD_DEPLOY_DIR:-/home/admin/new_api-test}"

if [ "$(pwd)" != "$STANDARD_DEPLOY_DIR" ]; then
  echo "Warning: standard new_api test deploy directory is $STANDARD_DEPLOY_DIR; current directory is $(pwd)." >&2
fi

mkdir -p data logs

docker compose --project-name "$PROJECT_NAME" -f "$COMPOSE_FILE" up -d
docker compose --project-name "$PROJECT_NAME" -f "$COMPOSE_FILE" ps

curl -fsS http://127.0.0.1:3002/api/status >/dev/null
echo "new_api test health check passed"
