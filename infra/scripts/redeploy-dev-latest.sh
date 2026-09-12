#!/bin/sh
set -eu

DEPLOY_DIR="${DEPLOY_DIR:-/home/admin/gemshin_nb-test/app}"
REF="${REF:-dev}"
REMOTE="${REMOTE:-origin}"
FORCE=0
WITH_NEWAPI=0
NEWAPI_DIR="${NEWAPI_DIR:-/home/admin/new_api-test}"

usage() {
  cat <<'EOF'
Usage: infra/scripts/redeploy-dev-latest.sh [options]

Redeploy gemshin_nb test environment from the latest remote ref.

Options:
  --dir <path>          Gemshin test deploy directory.
                       Default: /home/admin/gemshin_nb-test/app
  --ref <ref>           Branch, tag, or commit to deploy. Default: dev
  --remote <name>       Git remote to fetch from. Default: origin
  --force               Discard local code changes before checkout.
  --with-newapi         Also refresh and restart /home/admin/new_api-test.
  --newapi-dir <path>   new_api test deploy directory.
                       Default: /home/admin/new_api-test
  -h, --help            Show this help.

Examples:
  ./infra/scripts/redeploy-dev-latest.sh
  ./infra/scripts/redeploy-dev-latest.sh --force
  ./infra/scripts/redeploy-dev-latest.sh --ref dev --with-newapi
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dir)
      shift
      DEPLOY_DIR="${1:?Missing value for --dir}"
      ;;
    --ref)
      shift
      REF="${1:?Missing value for --ref}"
      ;;
    --remote)
      shift
      REMOTE="${1:?Missing value for --remote}"
      ;;
    --force)
      FORCE=1
      ;;
    --with-newapi)
      WITH_NEWAPI=1
      ;;
    --newapi-dir)
      shift
      NEWAPI_DIR="${1:?Missing value for --newapi-dir}"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [ ! -d "$DEPLOY_DIR/.git" ]; then
  echo "Missing git repository at $DEPLOY_DIR" >&2
  exit 1
fi

cd "$DEPLOY_DIR"

if [ "$FORCE" -eq 1 ]; then
  echo "Force mode: discarding local code changes in $DEPLOY_DIR"
  git reset --hard
  git clean -fd -e .env -e .env.dev -e ".env.*"
elif [ -n "$(git status --porcelain)" ]; then
  echo "Refusing to deploy because $DEPLOY_DIR has local changes." >&2
  echo "Review them first, or rerun with --force to discard local code changes." >&2
  git status --short >&2
  exit 1
fi

BEFORE_COMMIT="$(git rev-parse HEAD)"
echo "Fetching $REMOTE ..."
git fetch --prune "$REMOTE"

if git show-ref --verify --quiet "refs/remotes/$REMOTE/$REF"; then
  TARGET_REF="$REMOTE/$REF"
  TARGET_COMMIT="$(git rev-parse "$TARGET_REF^{commit}")"
  git checkout -B "$REF" "$TARGET_COMMIT"
else
  TARGET_REF="$REF"
  TARGET_COMMIT="$(git rev-parse "$TARGET_REF^{commit}")"
  git checkout --detach "$TARGET_COMMIT"
fi

echo "Deploying gemshin_nb test:"
echo "  directory: $DEPLOY_DIR"
echo "  ref:       $TARGET_REF"
echo "  before:    $BEFORE_COMMIT"
echo "  target:    $TARGET_COMMIT"

chmod +x infra/scripts/deploy-dev.sh
./infra/scripts/deploy-dev.sh

if [ "$WITH_NEWAPI" -eq 1 ]; then
  mkdir -p "$NEWAPI_DIR"
  cp infra/new_api-test/docker-compose.yml "$NEWAPI_DIR/docker-compose.yml"
  chmod +x infra/scripts/deploy-newapi-test.sh
  cd "$NEWAPI_DIR"
  "$DEPLOY_DIR/infra/scripts/deploy-newapi-test.sh"
fi

echo "Public health check:"
curl -fsS https://dev.991hahahanxsm.xyz/api/v1/health/
echo
echo "Redeploy finished."
