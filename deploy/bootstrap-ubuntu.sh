#!/usr/bin/env bash
# One-time setup of the ATS Auditor deploy account on the VPS.
#
#   sudo DEPLOY_PUBKEY='ssh-ed25519 AAAA... github-actions-ats' ./deploy/bootstrap-ubuntu.sh
#
# Idempotent: safe to re-run to refresh the gate script or the authorised key.
# Review before running.
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then echo 'Run with sudo' >&2; exit 1; fi
command -v apt-get >/dev/null || { echo 'This script targets Ubuntu/Debian' >&2; exit 1; }
: "${DEPLOY_PUBKEY:?set DEPLOY_PUBKEY to the public half of the GitHub deploy key}"

here=$(cd "$(dirname "$0")" && pwd)

apt-get update
apt-get install -y ca-certificates curl git docker.io
if ! docker compose version >/dev/null 2>&1; then
  apt-get install -y docker-compose-v2 || {
    echo 'Docker Compose v2 unavailable; follow the official Docker instructions.' >&2
    exit 1
  }
fi
systemctl enable --now docker

# Dedicated, passwordless, shell-less-by-key account. Membership in `docker`
# is root-equivalent; the forced command below is what limits the key.
id atsdeploy >/dev/null 2>&1 ||
  useradd --create-home --home-dir /home/atsdeploy --shell /bin/bash --user-group atsdeploy
usermod -aG docker atsdeploy
passwd -l atsdeploy >/dev/null

install -o root -g root -m 755 "$here/ats-deploy.sh" /usr/local/sbin/ats-deploy

install -d -o atsdeploy -g atsdeploy -m 755 /opt/ats-auditor
install -d -o atsdeploy -g atsdeploy -m 755 /opt/ats-auditor/production /opt/ats-auditor/staging

install -d -o atsdeploy -g atsdeploy -m 700 /home/atsdeploy/.ssh
printf 'command="/usr/local/sbin/ats-deploy",restrict %s\n' "$DEPLOY_PUBKEY" \
  > /home/atsdeploy/.ssh/authorized_keys
chown atsdeploy:atsdeploy /home/atsdeploy/.ssh/authorized_keys
chmod 600 /home/atsdeploy/.ssh/authorized_keys

echo 'Deploy account ready. Next: add the atsmcp.yashcodes.com block to the Caddy'
echo 'config on the host and set the VPS_* GitHub secrets (see deploy/README.md).'
