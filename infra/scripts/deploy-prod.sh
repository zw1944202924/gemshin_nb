#!/bin/sh
set -eu

ENV_FILE="${ENV_FILE:-.env.production}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-gemshin_nb}"
STANDARD_DEPLOY_DIR="${STANDARD_DEPLOY_DIR:-/home/admin/gemshin_nb-prod}"
export GEMSHIN_ENV_FILE="$ENV_FILE"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE. Copy .env.production.example and fill production secrets first." >&2
  exit 1
fi

if [ "$(pwd)" != "$STANDARD_DEPLOY_DIR" ]; then
  echo "Warning: standard production deploy directory is $STANDARD_DEPLOY_DIR; current directory is $(pwd)." >&2
fi

docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d mysql redis
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d api web
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py migrate
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py seed_modules
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py seed_roles
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
