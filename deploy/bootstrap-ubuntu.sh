#!/usr/bin/env bash
# Run manually via sudo on your own Ubuntu server. Review first.
set -euo pipefail
if [ "$(id -u)" -ne 0 ]; then echo 'Run with sudo' >&2; exit 1; fi
if ! command -v apt-get >/dev/null; then echo 'This script is for Ubuntu/Debian only' >&2; exit 1; fi
apt-get update
apt-get install -y ca-certificates curl git docker.io
if ! docker compose version >/dev/null 2>&1; then
  apt-get install -y docker-compose-v2 || { echo 'Docker Compose v2 unavailable in current OS repositories; follow official Docker installation instructions.' >&2; exit 1; }
fi
systemctl enable --now docker
mkdir -p /opt/ats-auditor/production /opt/ats-auditor/staging
# GitHub Actions deploy user must have docker permission (root-equivalent).
# Grant deliberately after verifying SSH key-only access and audit policy.
echo 'Docker installed. Configure restricted SSH deployment user, GitHub secrets and Caddy manually.'
