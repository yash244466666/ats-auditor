# AGENT.md — ATS Auditor Project Context and Operating Rules

> Repository-wide context for AI coding agents and human maintainers. Read this file before modifying code, pipelines, benchmarks or documentation. Claude Code also reads [CLAUDE.md](CLAUDE.md); agents that auto-discover AGENTS.md can use [AGENTS.md](AGENTS.md).
>
> Verified baseline: 2026-11-02 (Asia/Dhaka). Status and remote availability can change. Before reporting anything as current, inspect GitHub, the relevant Actions runs and, when appropriate, the live service. [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) is a dated snapshot, not a real-time monitor.

## 1. Mission, scope and non-goals

**ATS Auditor** is an independent, MIT-licensed, Python-based resume-to-job-description matching project with a CLI, FastAPI development interface and a self-hosted, ChatGPT-compatible Model Context Protocol (MCP) server.

The goal is to produce inspectable, reproducible **heuristic** matching signals: job keyword coverage, missing requirements, contextual evidence, warnings and concrete improvements. It is **not** a real employer ATS, hiring-decision predictor, verified eligibility checker or exact clone of any commercial provider. Prior Upplai interactions were black-box research, not access to its internals. Never claim proprietary parity.

Keep three concepts separate:
1. **Compatibility estimate:** an experimentally calibrated approximation of observed third-party numeric behavior; not source parity.
2. **Evidence quality:** whether the resume demonstrates the named skills in actual work/project context, with resistance to keyword stuffing.
3. **Requirements fit:** a separate, transparent match against recognized job requirements.

Recommend truthful resume changes; do not invent employers, projects, technologies, credentials, dates, achievements or performance metrics. Use fictional/redistributable examples for every public test, benchmark, issue and demo. Numeric scoring must come from code execution, not intuition.

## 2. Current verified operational state

- Repository: https://github.com/yash244466666/ats-auditor
- Python distribution/application version: **0.4.0** in pyproject.toml. The separately distributed **private ChatGPT skills plugin** was documented at **0.4.1**; those are different release surfaces.
- Production MCP URL: https://atsmcp.yashcodes.com/mcp (Streamable HTTP through Caddy).
- Health URL: https://atsmcp.yashcodes.com/health.
- Production host: Ubuntu/Debian VPS identified in deployment docs as **vps-2**, IP 140.238.208.16.
- Latest baseline checked while authoring this file: main commit **afd7eca938ddee6643545270b2158390209151de** had passing CI and VPS deployment runs; dev commit **1c5caafec5c5fd1eca45a377cadc25a865f45298** had passing CI. Do not treat these SHAs as permanent release pointers.
- Both ChatGPT-connected MCP tools were called successfully with *fictional* resume and job text after the response-format fix in PR #11. An independently documented over-the-wire MCP initialize/list/call and public health check also exist in docs/PROJECT_STATUS.md.
- The endpoint is **PUBLIC AND UNAUTHENTICATED** as documented in SECURITY.md. The owner has explicitly **deferred authentication to a later milestone**. This is an open security limitation, not a resolved feature or license to send real applicant data.

Prioritize correctness, scoring validity, testing, docs and functionality according to the task. Do not silently introduce authentication in an unrelated change; do not remove or downplay security warnings.

## 3. Read these sources before changing behavior

1. README.md — current features, examples, limitations.
2. docs/PROJECT_STATUS.md — dated production and integration checks.
3. SECURITY.md — privacy and current public-exposure limitations.
4. CONTRIBUTING.md — contribution and benchmark standards.
5. deploy/README.md — actual VPS, branching, SSH and Caddy operations.
6. benchmarks/INDEPENDENT_VALIDATION.md and benchmarks/CALIBRATION_REPORT.md — calibration evidence and methodological caveats.
7. docs/REVERSE_ENGINEERING.md — observations vs hypotheses about external tools.

Some benchmark write-ups are historical and may still mention an older, untested MCP deployment. Use the actual current code, CI and deploy docs to resolve operational status; preserve the older experimental results as historical data.

## 4. Architecture and ownership of each module

| Path | Responsibility |
| --- | --- |
| pyproject.toml | Package metadata, dependency and SDK compatibility bounds, CLI entry points, pytest config. |
| src/ats_auditor/engine.py | Canonical score_resume dispatcher, keyword catalog, legacy-frequency and evidence heuristics, formatting and stuffing checks. |
| src/ats_auditor/source_approx.py | Broad vocabulary, empirical calibration and compatibility score. |
| src/ats_auditor/requirement_fit.py | Independent weighted requirements coverage with contextual evidence credit. |
| src/ats_auditor/service.py | ATSService.analyze validation, result IDs, local session state and format_report output. |
| src/ats_auditor/api.py | FastAPI local/dev UI and JSON endpoints with optional ATS_API_KEY protection. |
| src/ats_auditor/static/index.html | Static browser UI served by the FastAPI app. |
| src/ats_auditor/cli.py | Text-file CLI (currently compatibility/evidence selections). |
| src/ats_auditor/mcp_server.py | FastMCP server, tool registration, production statelessness, text + structured MCP responses. |
| tests/ | Scoring, calibration, HTTP, safety, deployment and in-process MCP transport regressions. |
| benchmarks/ | Fictional resumes, public-job-derived briefs, calibration scripts and recorded comparisons. |
| examples/ | Synthetic text fixtures and intentional anti-stuffing stress test. |
| .github/workflows/ci.yml | Python 3.11–3.13 tests, MCP construction, Docker build/start/health test. |
| .github/workflows/deploy.yml | Successful-push-CI-gated deployment to VPS with pinned SSH host verification. |
| deploy/compose.yml | Loopback-only MCP service containers and runtime restrictions. |
| deploy/Caddyfile | Public HTTPS /health and /mcp reverse proxy (no auth yet). |
| deploy/ats-deploy.sh | Server-side forced-command deployment gate. |
| deploy/bootstrap-ubuntu.sh | Ubuntu/Debian deploy-account and Docker/bootstrap provisioning. |
| scripts/sync-branches.sh | Protected-branch synchronization via GitHub merge API. |

Core call paths:

- CLI -> ATSService.analyze -> engine.score_resume -> mode-specific scoring -> format_report.
- HTTP POST /v1/score or /v1/get_resume_ats_score -> FastAPI ScoreRequest -> ATSService.analyze (local/development session semantics).
- MCP tool -> score_safely -> fresh ATSService (production) or shared local SERVICE (development) -> CallToolResult with both TextContent and structuredContent.
- MCP health GET /health -> FastMCP custom Starlette route (not the FastAPI server's separate health implementation).

### Input and response invariants

- Full resume and job description: at least **100** and **50** non-whitespace characters respectively. Validate before modifying cached local session state.
- Valid session ID: 1–128 characters. Local session cache max age **1 hour** and max **100** session entries; neither cache keys nor session_id establish authentication.
- score_resume modes: compatibility, evidence, legacy_frequency and requirement_fit. The CLI currently advertises compatibility/evidence; the FastAPI ScoreRequest advertises compatibility/evidence/requirement_fit; MCP get_resume_ats_score accepts scoring_mode and defaults to compatibility. Match interfaces to actual code rather than assuming feature parity.
- Output contract includes overall_score (0–100), keyword_coverage, keywords with keyword/present/importance/score, details; service responses add id, job_description_id and content.
- MCP **must** return a protocol-valid CallToolResult with a useful human-readable TextContent element and populated structuredContent. The original bug returned {} in ChatGPT. Preserve both fields and the regression tests.
- In ATS_DEPLOYMENT_MODE=production, MCP scoring must require complete resume_text **and** job_description on every call; reject job_description_id-only reuse. A fresh service/UUID scopes each call. Do not reintroduce cross-caller shared state.

## 5. Local development and verification

Use a modern Python version covered by CI (3.11, 3.12 or 3.13; the package declares >=3.10). From repository root:

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -e '.[dev,mcp]'
    pytest -q
    python -m compileall -q src

CLI:

    ats-auditor --resume examples/synthetic_resume.txt --job examples/truey_job.txt --mode compatibility
    ats-auditor --resume examples/synthetic_resume.txt --job examples/truey_job.txt --mode evidence --json

Development HTTP API/UI:

    uvicorn ats_auditor.api:app --host 127.0.0.1 --port 8787

Container smoke test:

    docker build --pull -t ats-auditor:local .
    docker run --rm -p 127.0.0.1:8000:8000 ats-auditor:local

Then, separately, curl http://127.0.0.1:8000/health. In production mode the Docker image is an **MCP** server, not the FastAPI UI. The MCP dependency is pinned to mcp>=1.28,<2 because the current FastMCP code depends on the 1.x API. Any SDK upgrade requires an explicit migration and MCP client-tool tests.

Always run targeted tests for modified code and the full suite before a release. For MCP changes, ensure tests/test_mcp_server.py calls **both** tools over a connected in-memory MCP client and asserts real text plus structured scores; server startup and HTTP /health alone do not prove scoring tools work. For deployments, run Docker smoke checks and preserve the expected non-root UID/GID **10001:10001**.

## 6. Git branches, CI/CD and release discipline

- Develop on **dev** or a feature branch. **main** is protected, PR-only with linear history; required checks: Python 3.11, Python 3.12, Python 3.13 and Docker build.
- Pushes and PRs trigger CI. Only a **successful CI push** on main/dev from this repository triggers deployment; PR CI must never deploy. Deploys are serialized through a shared concurrency group because the VPS has about 1 GB RAM.
- dev CI success -> staging, server-local **127.0.0.1:8801**. main CI success -> production, **127.0.0.1:8800**. Caddy exposes only production, not staging.
- Promote changes through a PR to main; repository deploy guide recommends **Squash and merge** for its branch rules. Review diff and check status before merging. Do not force-push, bypass checks, leak credentials or push directly to main.
- After a main merge, synchronize the development branch following scripts/sync-branches.sh (GitHub CLI and a clean repo are needed); verify that dev-only content is not silently overwritten. GitHub API merges are used instead of forbidden force-pushes.
- CI/deployment red/green states and container health are different from actual end-to-end public MCP functionality. Record each evidence source separately.

### VPS deployment path and security boundaries

- GitHub encrypted secrets: VPS_HOST, VPS_USER, VPS_SSH_KEY, VPS_SSH_KNOWN_HOSTS; optional VPS_SSH_PORT (22). No secrets in git, docs, logs, fixture payloads or chat.
- Deployment identity: **atsdeploy** with a key restricted through the forced command at /usr/local/sbin/ats-deploy; it is not a regular interactive SSH shell. The former password/sshpass scheme is obsolete and must not be reintroduced.
- The action checks out the exact tested commit and streams *git-tracked* files as a tarball via SSH. The VPS gate accepts only deploy production or deploy staging, updates /opt/ats-auditor/<environment>, rebuilds Docker Compose and verifies loopback /health.
- Compose uses a non-root image, read-only root FS, temporary /tmp, dropped capabilities and loopback-only host ports. The deploy account is still in the docker group, which is effectively root-equivalent; do not mistake the forced-command restriction for perfect isolation.
- Caddy proxies https://atsmcp.yashcodes.com/health and /mcp* to production, with a 2 MB MCP request-body cap and unbuffered SSE. The current Caddyfile does **not** authenticate clients or return 403 to unauthenticated requests.
- Caddy's active config on the VPS is a separately managed bind-mounted host file. Do not assume editing deploy/Caddyfile alone applies to the server. Read deploy/README.md before modifying/reloading it.
- Do not run arbitrary destructive commands or expose staging/container ports on public interfaces. Never disable StrictHostKeyChecking or print private keys.

## 7. Data ethics, benchmarking and evaluation rules

- The [public SkillSpan adapter](benchmarks/public_skillspan/README.md) evaluates uncapped existing vocabulary spans against external expert annotations, not complete scoring modes or hiring accuracy. Cache downloaded job annotations outside tracked source; pin and verify hashes, preserve official/diagnostic split results, and record protocols before evaluation. Unit tests remain fictional and offline. Do not tune against observed test results and continue calling them untouched.

- Use **fictional data** in repository tests and demos. Do not copy real resumes or applicant identities into tracked files, prompts, public logs or PRs.
- Do not call scores 'ATS pass rates', guaranteed interview chances, employer eligibility determinations or a faithful replication of Upplai's private algorithms.
- Existing v0.4 calibration report: 12 fictional resume/job pairs had an **inspected/calibrated** mean absolute error of **4.67 points**, with a **22-point** worst mismatch, relative to observed external tool output. It is **not** blind validation or a generalization guarantee.
- Keep benchmark calibration data separate from holdouts; report sample size, scoring mode, MAE, worst error, job family variation and known selection bias. Preserve negative/mismatched cross-role examples.
- Evaluate contextual project evidence, missing requirements and repetition sensitivity independently. Never optimize just for keyword stuffing or an impressive score.
- Eligibility, work authorization, location, visa, salary, seniority and actual document/PDF/DOCX parseability are **not** proven by a text-only keyword score.
- Use reproducible deterministic tests, document assumptions and failure cases, and avoid copying proprietary test corpora without permission.

## 8. Current limitations and roadmap

**Known limitations:** public MCP has no authentication/authorization; missing per-user identity and rate limiting; production processes full textual inputs; no first-class binary PDF/DOCX extraction/layout validation; limited industry vocabulary and benchmark diversity; calibrated compatibility score may diverge substantially from external results; no guarantee of automated rollback, backup or 24/7 availability.

**Planned work:** stronger independent, untouched holdout validation; clearer scores and gap explanations; richer import and document analysis; improved operator observability and reliability. **OAuth 2.1 / suitable client authentication, tenant identity, quotas and privacy controls are deferred by project-owner decision**, but remain required before private production data is accepted. Do not present this deferment as a security approval.

## 9. AI-agent execution checklist

For every substantive change:
1. **Inspect** current branch, repository HEAD, relevant implementation, tests and existing docs; do not rely solely on a dated summary.
2. **Scope** changes to the requested behavior. State user-visible trade-offs and security implications; do not silently change scores, auth posture or deployment routes.
3. **Implement** readable, auditable Python with explicit input contracts and minimal third-party dependencies. Avoid new LLM/network dependencies without a clear need.
4. **Test** the relevant unit, integration and MCP tool-call path with synthetic data; run the full pytest/compile and Docker checks when feasible. If tests cannot be run, disclose this explicitly.
5. **Update** README, docs/PROJECT_STATUS.md, deploy/README.md, SECURITY.md or benchmarks when public behavior, score calibration, deployments or security posture changes. Keep agent docs aligned with actual architecture.
6. **Release** using protected-branch PR checks; verify merge commit, CI result, deployment job and health/tool behavior as applicable. Never describe an in-progress run as successful.
7. **Report** exact files changed, tests run, verified commit/PR/Actions links and remaining blockers. Do not claim a credential, remote operation or security control was configured without evidence.

When unsure, prefer a transparent limitation and a small verified change over a fabricated metric or unverified deployment claim.
