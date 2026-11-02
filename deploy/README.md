# VPS deployment for ATS Auditor

Live at **https://atsmcp.yashcodes.com/mcp** (MCP streamable-http) on `vps-2`.
Health probe: `https://atsmcp.yashcodes.com/health`.

**Verified 2026-11-02:** [`main` CI run 41349223958](https://github.com/yash244466666/ats-auditor/actions/runs/41349223958) and [production deploy run 41349261322](https://github.com/yash244466666/ats-auditor/actions/runs/41349261322) both succeeded for commit `d74350bf`. A connected ChatGPT MCP tool call returned structured scores for both `get_resume_ats_score` and `compare_resume_quality` with fictional inputs, after [PR #11](https://github.com/yash244466666/ats-auditor/pull/11). This is not a continuous external uptime check.

**Authentication is not yet implemented:** the public `/mcp` endpoint is unauthenticated. Do **not** send real resumes or confidential job information until a future authentication/authorization milestone. See [SECURITY.md](../SECURITY.md) and [dated project status](../docs/PROJECT_STATUS.md).

## Branch policy

- `dev`: CI passes -> deploy to staging on VPS loopback `127.0.0.1:8801`.
- `main`: CI passes -> deploy to production on VPS loopback `127.0.0.1:8800`,
  published by Caddy at `atsmcp.yashcodes.com`.
- Deploys occur only after the matching **push** CI run is successful
  (`workflow_run`), and the workflow checks out *that exact commit*.
- `main` is pull-request-only (CI required, linear history, no force-push or
  deletion). `dev` requires the same CI and blocks force-push/deletion for
  everyone, while the repository owner keeps the ability to push directly.
- Synchronize release changes back into `dev` after merging to protected `main`. Use
  `scripts/sync-branches.sh`; it synchronizes using GitHub's merge API rather
  than force-pushing or assuming the branches share identical commit SHAs.
- Merge a release with **Squash and merge**. Once `dev` carries a sync merge
  commit, GitHub refuses a rebase merge ("This branch can't be rebased"), and a
  merge commit is refused by `main`'s linear-history rule.

## How a deploy runs

1. Push to `dev` (or `main`) -> **CI** (`ci.yml`) runs pytest on 3.11/3.12/3.13,
   including in-process client calls against both MCP scoring tools. It also
   constructs the MCP server, builds + starts the Docker image, and hits
   `/health` inside it.
2. On CI success, **Deploy to VPS** (`deploy.yml`) checks out the tested SHA,
   streams `git ls-files` as a tarball over SSH, and the server-side gate
   builds and starts the compose project.
3. The gate waits up to two minutes for `http://127.0.0.1:<port>/health` and
   fails the job (with container logs) if it does not come up.

## Server-side layout (vps-2)

| Path | Purpose |
|---|---|
| `/opt/ats-auditor/production` | release tree for `main` |
| `/opt/ats-auditor/staging` | release tree for `dev` |
| `/opt/ats-auditor/deploy.log` | append-only deploy log |
| `/usr/local/sbin/ats-deploy` | forced-command gate (from `deploy/ats-deploy.sh`) |
| `/home/atsdeploy/.ssh/authorized_keys` | one key, `command="/usr/local/sbin/ats-deploy",restrict` |

The deploy account `atsdeploy` is in the `docker` group (required to run
compose, and therefore root-equivalent on this host). Its SSH key is
**forced-command only**: it can never open a shell, forward ports, or write
outside the two release directories. Install/refresh the gate with:

```sh
sudo install -o root -g root -m 755 deploy/ats-deploy.sh /usr/local/sbin/ats-deploy
```

## Server bootstrap (Ubuntu/Debian)

`deploy/bootstrap-ubuntu.sh` creates everything the workflow expects: Docker
and Compose v2, the `atsdeploy` account (locked password, `docker` group), the
two release directories, the forced-command gate at
`/usr/local/sbin/ats-deploy`, and one `authorized_keys` line for the deploy
key.

```sh
# on the VPS, from a checkout of this repository
sudo DEPLOY_PUBKEY="$(cat ~/.ssh/ats-deploy-ed25519.pub)" ./deploy/bootstrap-ubuntu.sh
```

It is idempotent — re-run it to refresh the gate after editing
`deploy/ats-deploy.sh`. The public Caddy block is host-specific and applied by
hand (see below).

## GitHub secrets

Repository (or per-environment) **encrypted** secrets:

- `VPS_HOST`: `140.238.208.16`
- `VPS_USER`: `atsdeploy`
- `VPS_SSH_PORT`: optional, defaults to `22`
- `VPS_SSH_KEY`: the private half of the deploy keypair
- `VPS_SSH_KNOWN_HOSTS`: one line, `<host> ssh-ed25519 <host-key-base64>`

Get the verified host key from the server itself:

```sh
ssh -i <key> <admin>@<host> 'sudo cat /etc/ssh/ssh_host_ed25519_key.pub'
```

Strict host-key checking is always on. Rotate `VPS_SSH_KEY` by generating a
new keypair, updating the single `authorized_keys` line, and replacing the
secret.

## Caddy

`deploy/Caddyfile` mirrors the `atsmcp.yashcodes.com` block on vps-2. It proxies
only `/health` and `/mcp*` to `127.0.0.1:8800`, caps request bodies at 2 MB, and
disables response buffering so MCP's SSE stream is not held back. Staging is
never published; tunnel it instead:

```sh
ssh -N -L 8801:127.0.0.1:8801 <admin>@140.238.208.16
```

Apply a Caddy change on the VPS by appending in place (`tee -a`, never
`sed -i` — the file is a single-file bind mount and `sed -i` swaps the inode),
then:

```sh
docker exec caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
docker exec caddy caddy reload   --config /etc/caddy/Caddyfile --adapter caddyfile
```

## Dependency note

The [public SkillSpan benchmark](../benchmarks/public_skillspan/README.md) is a local/offline evaluation tool, not a production service. It introduces no runtime dependency or VPS task. Do not download corpora onto the VPS or send applicant data to the unauthenticated MCP endpoint for benchmark work. CI tests the adapter using fictional inputs without network downloads.

`pyproject.toml` pins `mcp>=1.28,<2`. The server uses `FastMCP`; mcp 2.x renamed
it to `MCPServer` and the container exits at import time. CI starts the
built image, calls `/health`, and exercises real in-memory MCP client tool calls
that assert nonempty readable and structured scoring results. MCP results use
`CallToolResult` with `TextContent` and `structuredContent` to support clients
that consume either representation.
