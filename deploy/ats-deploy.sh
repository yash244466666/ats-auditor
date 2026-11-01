#!/usr/bin/env bash
# Forced-command entry point for GitHub Actions on the VPS.
#
# Installed root-owned at /usr/local/sbin/ats-deploy and referenced from
# /home/atsdeploy/.ssh/authorized_keys as:
#   command="/usr/local/sbin/ats-deploy",restrict ssh-ed25519 AAAA... github-actions
#
# The client runs `ssh atsdeploy@host "deploy <env>"`; sshd puts that string in
# SSH_ORIGINAL_COMMAND and runs this script instead of a shell, so the deploy
# key can never open a shell, forward ports, or touch anything outside the two
# release directories below.
#
# A tarball of `git ls-files` for the already-tested commit arrives on stdin.
set -euo pipefail

ENV_NAME=""
case "${SSH_ORIGINAL_COMMAND:-}" in
  "deploy production") ENV_NAME=production; PORT=8800 ;;
  "deploy staging")    ENV_NAME=staging;    PORT=8801 ;;
  *)
    echo "refused: expected 'deploy production' or 'deploy staging'" >&2
    exit 64
    ;;
esac

ROOT="/opt/ats-auditor/$ENV_NAME"
LOG="/opt/ats-auditor/deploy.log"
STAGE="$(mktemp -d /tmp/ats-deploy.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT

log() { printf '%s [%s] %s\n' "$(date -u +%FT%TZ)" "$ENV_NAME" "$*" | tee -a "$LOG"; }

log "receiving tarball"
tar -xzf - -C "$STAGE"
if [[ ! -f "$STAGE/deploy/compose.yml" ]]; then
  echo "refused: tarball has no deploy/compose.yml" >&2
  exit 65
fi

# Replace the tree so files deleted upstream actually disappear.
install -d -o "$(id -u)" -g "$(id -g)" "$ROOT"
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$STAGE"/. "$ROOT"/

cd "$ROOT"
log "building and starting (port $PORT)"
COMPOSE_PROJECT_NAME="ats-$ENV_NAME" PUBLISH_PORT="$PORT" \
  docker compose -f deploy/compose.yml up -d --build --remove-orphans
COMPOSE_PROJECT_NAME="ats-$ENV_NAME" PUBLISH_PORT="$PORT" \
  docker compose -f deploy/compose.yml ps

for _ in $(seq 1 40); do
  if curl --fail --silent --max-time 3 "http://127.0.0.1:$PORT/health" >/dev/null; then
    log "healthy on 127.0.0.1:$PORT"
    exit 0
  fi
  sleep 3
done

log "health check failed"
COMPOSE_PROJECT_NAME="ats-$ENV_NAME" PUBLISH_PORT="$PORT" \
  docker compose -f deploy/compose.yml logs --tail=60 mcp >&2 || true
exit 1
