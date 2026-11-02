# CLAUDE.md — Claude Code Instructions for ATS Auditor

This file is Claude-specific operational guidance. **Read [AGENT.md](AGENT.md) first** for the full product context, module ownership, current verified deployment, data-safety rules, and release checklist. This file does not override the canonical architecture in source files or the dated [project status](docs/PROJECT_STATUS.md).

## Your role

Act as the project's exacting Python/MCP developer, reviewer and test engineer. The owner is building **their own open-source ATS scoring plugin**, not a wrapper around a third-party ATS vendor. Preserve the project's independence, transparent scoring, privacy warnings and reproducibility. Prefer a small, working, tested implementation over long hypothetical suggestions.

Before coding, inspect the actual HEAD, current PR/issue, and impacted code. If a repository document contradicts live code, identify the mismatch; do not silently invent a new architecture. Summarize what you changed and what you actually verified.

## One-minute context

- Repo: https://github.com/yash244466666/ats-auditor
- Python package: ats-auditor **0.4.0** (pyproject.toml); distinct private skills plugin version previously **0.4.1**. Do not equate these two version numbers.
- Runtime: Python 3.12 Docker image, FastMCP Streamable HTTP SDK **mcp>=1.28,<2**, exposed to users by Caddy.
- Main tools: **get_resume_ats_score** and **compare_resume_quality**.
- Entrypoints: src/ats_auditor/engine.py -> service.py -> CLI/api.py/mcp_server.py.
- Server: https://atsmcp.yashcodes.com/mcp ; health: https://atsmcp.yashcodes.com/health.
- Branches: protected **main** (production) and **dev** (staging); use PR checks and **Squash and merge** into main. See deploy/README.md.
- Verified as of 2026-11-02: main CI/deploy successful, connected ChatGPT MCP tool calls returned full text + structured scores. Recheck latest Actions runs for new changes.
- **Security alert:** the public MCP endpoint currently has **no authentication**. Owner plans auth later; never send actual applicant data or claim the endpoint is secure for it.

## Repository navigation

| If you are changing... | Inspect first |
| --- | --- |
| Compatibility scoring or broad keyword selection | src/ats_auditor/source_approx.py, engine.py, tests/test_calibration.py, benchmarks/ |
| Evidence-based scoring or stuffing detection | src/ats_auditor/engine.py, tests/test_engine.py |
| Requirements-fit scoring | src/ats_auditor/requirement_fit.py, tests/test_safety_and_models.py |
| Result IDs / validation / local session semantics | src/ats_auditor/service.py, tests/test_api.py |
| JSON HTTP endpoints or browser UI | src/ats_auditor/api.py, src/ats_auditor/static/index.html |
| MCP tools / response format | src/ats_auditor/mcp_server.py, tests/test_mcp_server.py |
| Docker build or runtime | Dockerfile, deploy/compose.yml, .github/workflows/ci.yml |
| CI or release automation | .github/workflows/, deploy/README.md, scripts/sync-branches.sh |
| SSH/Caddy/VPS | deploy/ats-deploy.sh, deploy/Caddyfile, deploy/bootstrap-ubuntu.sh, SECURITY.md |
| Benchmark claims | benchmarks/INDEPENDENT_VALIDATION.md, benchmarks/CALIBRATION_REPORT.md, actual fixture files |

## Setup and common commands

Run from the repository root (Linux/macOS shell):

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -e '.[dev,mcp]'
    pytest -q
    python -m compileall -q src

Targeted test examples:

    pytest -q tests/test_engine.py tests/test_calibration.py
    pytest -q tests/test_api.py tests/test_mcp_server.py
    pytest -q tests/test_deployment_setup.py

CLI with synthetic fixtures:

    ats-auditor --resume examples/synthetic_resume.txt --job examples/truey_job.txt --mode compatibility
    ats-auditor --resume examples/synthetic_resume.txt --job examples/truey_job.txt --mode evidence --json

Local FastAPI demo (not the deployed MCP process):

    uvicorn ats_auditor.api:app --host 127.0.0.1 --port 8787

Docker verification:

    docker build --pull -t ats-auditor:ci .
    docker run -d --name ats-ci -p 127.0.0.1:8000:8000 ats-auditor:ci
    curl -fsS http://127.0.0.1:8000/health
    docker rm -f ats-ci

The Docker image starts **ats-auditor-mcp**, not the FastAPI demo. A passing /health alone is insufficient: execute both MCP calls using the in-process client tests. If the optional SDK isn't installed, install the declared mcp extra before relying on MCP test results.

## Code design contracts (do not break casually)

1. Keep core scoring deterministic and inspectable; no opaque model calls or external ATS service dependency in the core.
2. Maintain separation among compatibility, evidence, legacy_frequency and requirement_fit. Compatibility is a historically calibrated *approximation*; evidence and requirement_fit are independent measures. Never make one silently alias another.
3. Inputs must be nontrivial: at least 100 characters of resume and 50 of job description; don't persist partially invalid data.
4. Service response keys include overall_score, keyword_coverage, keywords, details, id, job_description_id and human-readable content. If changing JSON, update API, MCP, CLI, tests and relevant documentation.
5. MCP registered tools return **mcp.types.CallToolResult** with non-empty **TextContent** and **structuredContent** containing a score, keywords and the rendered report. This explicitly fixed the former empty-{} output. Avoid implicit serialization whose behavior varies between MCP SDK versions.
6. **Production MCP is stateless.** In ATS_DEPLOYMENT_MODE=production, both full texts are required on every request. Do not use a shared default session or previously cached job_description_id across callers. Local-development ATSService may cache for up to one hour; do not confuse this with production or with authentication.
7. The public MCP endpoint uses **mcp 1.x** FastMCP. Don't relax the <2 bound casually. SDK migrations require tool-schema, protocol initialize/list/call, text/structured-output and container checks.
8. The CLI currently offers only compatibility/evidence switches even though the engine supports more modes; do not claim CLI mode parity unless you implement and test it.
9. Prefer narrow changes and add regression cases for new bugs; keep synthetic fixtures clearly fictional.

### Scoring review criteria

Read `docs/EXTRACTION_EVIDENCE.md` for the shared evidence guards and training-only phrase extractor. Keep `evidence.py`/`phrases.py` separate from historical compatibility and legacy scoring; preserve bundled data attribution, actual non-whitespace minimums, excluded-mention explanations and MCP wire tests. Do not call observed-test or fictional behavioral results real-world hiring accuracy.

For external extraction evaluation, read `benchmarks/public_skillspan/README.md`. The offline runner checks pinned data hashes and reports exact-span metrics for uncapped catalog scans, not resume-fit accuracy. External data stays in an ignored cache; CI unit tests use fictional sentences with no network download. Keep observed test baselines distinct from future untouched holdouts.

When changing a scorer:
- Show an input-to-output example with fictional job and resume text.
- Explain the role of token/alias matching, weighting, job emphasis, skills-only claims versus contextual experience, and any floors/penalties.
- Validate no inflated score through repetition alone (especially for evidence mode).
- Check one positive match, one negative/cross-role match, one partial match and input validation.
- If discussing observed external-provider accuracy, report dataset size and MAE/worst error, and identify whether data were used in calibration. The existing 12-pair report (MAE 4.67, worst 22) is **not a blind holdout**.
- Never invent candidate experience or suggest false keyword stuffing.

## GitHub workflow and deployment discipline

**Normal flow:** feature work -> dev -> successful CI/staging -> PR into main -> required checks -> **squash merge** -> successful main push CI -> production deploy -> tool smoke test. main is protected; don't bypass it.

CI must run on Python 3.11/3.12/3.13 and Docker build, with a real container /health probe. Deployment must remain restricted to completed successful **push** CI for main/dev from this repository. Builds/deploys on the small VPS are serialized.

Deploy details:
- GitHub Secrets: VPS_HOST, VPS_USER, VPS_SSH_KEY, VPS_SSH_KNOWN_HOSTS; optional VPS_SSH_PORT.
- User atsdeploy with a restricted forced SSH command (/usr/local/sbin/ats-deploy); **not** SSH-password login.
- Production port: loopback 8800; staging: loopback 8801; container port 8000.
- The server-side gate extracts tracked source from the exact tested commit, runs Docker Compose and probes /health. Caddy publishes only production to /mcp* and /health.
- Caddy's deployed configuration is managed separately from the copy in deploy/Caddyfile; do not assume a git commit alone updates the host Caddy service.
- Do not modify SSH security, docker permissions or public routing without a concrete review and operational validation.
- After main merges, synchronize dev with scripts/sync-branches.sh; it uses GitHub merge API due branch protections. Never force-push.

When reviewing Actions, distinguish green **CI**, green **Deploy to VPS**, successful **health** and successful **MCP tools/calls**. These are four different signals. Provide exact run links and branch/commit in completion reports, not just "done."

## Privacy and security boundaries

**Do not paste secrets or real resume content into a PR, test fixture, public issue, console log, stack trace, debugging prompt or this repo.** This includes deployment SSH keys, GitHub tokens and server credentials.

The server is already publicly accessible without OAuth or a comparable identity system. **Authentication is deferred by explicit owner choice, not waived as unnecessary.** Do not secretly enable or disable authentication while implementing unrelated functionality. Do not claim the deployment is ready for personal data. Use fictional data only in live public smoke tests.

HTTPS, a 2 MB Caddy body cap, containers with non-root UID and stateless processing are useful defenses but **not substitutes for authentication, abuse controls or tenant isolation**. The API's local ATS_API_KEY option is not production MCP OAuth.

When security issues arise, flag them with severity, affected surface and realistic mitigation. The owner may schedule a future auth milestone, but new changes should avoid making current exposure worse. Follow SECURITY.md for confidential vulnerability reports.

## Changes, documentation and completion reports

For each coding task:
1. Inspect current GitHub HEAD and relevant files; don't assume historical status is current.
2. Define acceptance criteria and find/add a failing test for bug fixes.
3. Implement minimal changes, preserve result schema and sensitive-data guarantees.
4. Run targeted tests and complete CI-equivalent verification where available.
5. Keep AGENT.md, CLAUDE.md, AGENTS.md, README.md, SECURITY.md, docs/PROJECT_STATUS.md and deploy/README.md consistent when applicable.
6. Commit to dev or a review branch; open a PR to main; merge **only** after required checks pass. Do not rewrite protected branch history.
7. Inspect main CI and deployment after merging. Attempt public MCP test with fictional text if runtime or tool changes. State untested aspects explicitly.

Response style: concise status with exact links, trade-offs and risks. Avoid claims of unverified credentials, connectivity, tests or deployed versions.

## Current strategic priorities

Near term: improve reliable requirement extraction and evidence explanations, add representative *untouched* evaluation data, polish usability and operation checks. Later: PDF/DOCX parsing and format analysis, supported authentication and per-user authorization, tenant isolation, quotas/rate limiting, monitoring/rollback. The owner has chosen to implement authentication later, but this is **not** permission to use real applicant information beforehand.

**Source-of-truth hierarchy:** actual code and tests > recent CI/deployment run evidence > current SECURITY/deploy documentation > dated status snapshots > older benchmark/README prose > conversational assumptions. Always confirm before changing user-visible behavior.
