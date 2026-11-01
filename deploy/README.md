# VPS deployment for ATS Auditor

## Branch policy

- `dev`: CI passes -> deploy to staging on VPS loopback `127.0.0.1:8801`.
- `main`: CI passes -> deploy to production on VPS loopback `127.0.0.1:8800`.
- Require PR review/CI for `main`; ideally PRs from `dev` only.
- Deploys occur only after the matching CI push workflow is successful.
- The workflow checks out *the exact tested commit* and uses pinned SSH host keys.
- Both environments are docker-compose projects with separate containers.

## VPS prerequisites

1. Ubuntu/Debian VPS with SSH **public-key** login, Docker/Compose v2 and curl.
2. Create a minimally privileged deployment account; membership in `docker` grants
   root-equivalent access, so use a dedicated account and review its permissions.
3. Ensure SSH port is reachable from GitHub Actions, and allow inbound TCP 80/443
   for TLS. Do not expose Docker's loopback 8800/8801 on public interfaces.
4. Point DNS A record `atsmcp.yashcodes.com` to your VPS public IP.
5. Install Caddy, deploy `deploy/Caddyfile`, and provision HTTPS.
   **The Caddyfile deliberately returns 403 for public `/mcp`**. It is a
   safe deployment placeholder, not a usable public ChatGPT connection.
6. Production MCP mode is stateless and requires full resume and job text on
   every request; this prevents accidentally mixing callers through the default
   in-memory session ID. Add verified OAuth 2.1 or supported client mTLS trust
   before enabling public MCP.
   ChatGPT cannot present an arbitrary static API token in the connection.

## GitHub setup

Create a **public** repository with the MIT License included in the initial code commit, then push the included `main` and `dev` branches. Do not add credentials or real applicant data.
Configure branch protection: require CI on `main` and optionally on `dev`;
restrict direct pushes to main. Consider an explicit approval gate on the
`production` environment.

Set these *encrypted* repository / environment secrets:

- `VPS_HOST`: hostname or IP of your VPS
- `VPS_USER`: restricted SSH deployment username
- `VPS_SSH_PORT`: port number (normally `22`)
- `VPS_SSH_KEY`: contents of the dedicated ED25519 **private** deployment key
- `VPS_SSH_KNOWN_HOSTS`: verified SSH server public host key entry

Generate an **independent keypair**, install ONLY its `.pub` contents in
`~/.ssh/authorized_keys` on the VPS, store private key in GitHub Actions secrets,
then delete any extra workstation copies. Do not add passwords to repo, `.env`,
GitHub logs, commit history or workflow YAML. Never take `ssh-keyscan` at face
value; compare it to the fingerprint obtained from an authenticated VPS console.

## Bootstrap

Review `deploy/bootstrap-ubuntu.sh`, then run it as root (or install Docker
and Compose through your distribution's official instructions).

On the VPS create `/opt/ats-auditor/production` and
`/opt/ats-auditor/staging` owned by the deployment account.

Staging smoke test: `curl -f http://127.0.0.1:8801/health`
Production smoke test: `curl -f http://127.0.0.1:8800/health`

Main CI/build logs: GitHub Actions. Docker logs on VPS:
`docker compose -f /opt/ats-auditor/production/deploy/compose.yml logs --tail=50 mcp`.

## Security before launch

- Complete OAuth 2.1 authorization or verified client mTLS integration.
- Add per-user identity, tenant isolation and rate/size controls.
- Ensure no secrets or resume contents are logged.
- Implement backups/monitoring/rollback and a deployable image digest strategy.
- Change the disclosed VPS password as soon as safely possible; disable password SSH.
- Test ChatGPT MCP `list_tools` + scoring after server is accessible.

**Current status:** Source and workflow prepared; VPS not yet accessed or configured.
