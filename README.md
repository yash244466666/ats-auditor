# ATS Auditor — open-source resume–job scoring

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Open source:** MIT License; see [LICENSE](LICENSE), [CONTRIBUTING.md](CONTRIBUTING.md), and [SECURITY.md](SECURITY.md).

**Status:** v0.4.0 developer preview. This project is independently developed and is not affiliated with, endorsed by, or a copy of Upplai. Its estimated scores are heuristic and do not represent actual employer ATS decisions or predict hiring outcomes. The benchmark dataset is small and includes calibration cases; reported fit must not be mistaken for external validation.

**Safety:** Never upload real applicant resumes to public issues, pull requests, or benchmark fixtures. Use fictional data. The included MCP server is experimental and **must not be publicly accessible without robust authentication and tenant isolation**.

## GitHub and VPS release automation

See [`deploy/README.md`](deploy/README.md) for the `main` / `dev` pipelines, VPS bootstrap, DNS, Caddy TLS and required GitHub secrets. The public MCP endpoint is intentionally blocked pending OAuth or verified client mTLS. **Do not expose the private scoring service before authentication is configured.**

**Status:** Working, locally tested Python scoring engine + HTTP API; MCP adapter source included. The MCP dependency is listed but was not available for installation in this offline build environment, so the remote MCP transport is **not tested here**. This is an independent implementation, not a copy of Upplai's proprietary software.

The project implements a workflow similar to the observed Upplai tool:

1. Supply a full resume and a full job description.
2. Receive a 0–100 match score, weighted keywords, presence flags, keyword sub-scores, and recommendations.
3. Re-analyze an updated resume using `job_description_id`.
4. Reuse the most recent resume against a new job within the same **local-development** session. On production MCP, submit both texts on every request to isolate users.

It deliberately adds an **evidence mode** that discounts keyword stuffing, since external experiments showed Upplai's exposed score can reach 100 through repetition alone.

## Run locally (Python 3.10+)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
ats-auditor --resume examples/synthetic_resume.txt --job examples/truey_job.txt --mode compatibility
ats-auditor --resume examples/synthetic_resume.txt --job examples/truey_job.txt --mode evidence --json
uvicorn ats_auditor.api:app --host 127.0.0.1 --port 8787
```

Open `http://127.0.0.1:8787/` for the working **web interface**, or `/docs` for interactive Swagger API documentation.

### HTTP example

```bash
curl -s http://127.0.0.1:8787/v1/get_resume_ats_score \
  -H 'Content-Type: application/json' \
  -d '{"resume_text":"FULL RESUME TEXT...", "job_description":"FULL JOB DESCRIPTION...", "session_id":"my-local-profile"}'
```

Use **complete** texts rather than placeholders in real requests; the API rejects unusually short inputs.

### Upplai-compatible request patterns

```json
{"resume_text":"...full resume...", "job_description":"...full job...", "session_id":"alice"}
```

Updated resume for same job:

```json
{"resume_text":"...revised full resume...", "job_description_id":"<previous ID>", "session_id":"alice"}
```

New job using last resume:

```json
{"job_description":"...new full job description...", "session_id":"alice"}
```

Output includes `id`, `job_description_id`, `overall_score`, `keywords` and `content`, plus evidence and formatting assessments.

## Run as an MCP plugin (ChatGPT)

```bash
pip install -e '.[mcp]'
ats-auditor-mcp
```

The standard SDK should host Streamable HTTP MCP on port 8000, conventionally at `/mcp`. Confirm the route using MCP Inspector and your installed SDK version.

To connect ChatGPT, deploy behind **HTTPS and real authentication**, or use an approved secure tunnel. In ChatGPT web: Plugins → `+` → Add custom MCP server → enter your HTTPS `/mcp` endpoint → inspect tools → create plugin. The exact flow is subject to workspace permissions and product changes. See https://developers.openai.com/plugins/build/mcp-server and https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt.

The bundled MCP tool names are:

- `get_resume_ats_score` — compatible 3-primary-parameter workflow, optional `session_id`, `scoring_mode`.
- `compare_resume_quality` — evidence-based assessment that flags stuffing.

ChatGPT cannot connect directly to a `localhost` endpoint. The server must be accessible from ChatGPT by one of the supported secure methods. I have **not** deployed or registered this plugin.

## Scoring modes

**Compatibility (default)**: Expanded dictionary of requirements, missing keyword penalties, job-description frequency and title salience, tuned against observed third-party results for seven technical jobs. On 12 fictional-resume/job comparisons, development/inspected-validation MAE 4.67 points, with a worst observed difference of 22 points. This is NOT blind validation or exact Upplai parity.

**Legacy frequency** (`legacy_frequency`): Prior v0.2 count-based heuristic, preserved for backwards-compatible experiments.

**Evidence**: Rewards contextual project achievements, quantified results, and verified technical usage; repeated keywords alone receive limited additional credit and can incur a penalty. This mode is more suitable for resume optimization.

Neither is an actual employer ATS decision. Both work on extracted text, not on actual PDF/DOCX layout. Production layout analysis would need a separate document-parsing stage.

## Privacy and security

- The CLI and core do not send resumes to any external service or model.
- The HTTP and MCP servers are self-hosted; inputs stay on your infrastructure.
- Resume and job inputs are held in-process only, scoped by `session_id`, and expire after one hour of inactivity. Restarting the server clears them.
- **Do not expose the demo server publicly without authentication, per-user identity mapping, TLS, rate limiting, and audit rules.** `session_id` is not authentication.
- HTTP API supports a simple development `ATS_API_KEY` environment variable; production MCP should instead use robust OAuth or mTLS controls suited to the deployment.
- Example data is fictional. No user's personal resume is bundled.

## Limitations compared with Upplai

- Internal weights, model prompts, embedding methods, code, training data, and score normalization are not accessible, so exact output parity cannot be guaranteed.
- Only selected behavior is reverse engineered using black-box observations and public claims. A full benchmarking effort requires a labeled evaluation set, repeatability tests, rate-limit awareness, and comparisons across multiple job families.
- This replica does not yet parse binary PDF or DOCX, implement recruiter scoring, edit resumes, integrate with Google Drive, or provide a custom in-chat UI. Those are separate phases.
- Optional MCP adapter is provided as source. Validate it in an environment with the official MCP SDK installed before using it in ChatGPT.

For reproducible multi-resume observations, see `benchmarks/INDEPENDENT_VALIDATION.md`. For inferred scoring behavior, see `docs/REVERSE_ENGINEERING.md`.

## Reproduce the 100% failure mode (synthetic data only)

```bash
PYTHONPATH=src python examples/stress_test.py
```

This is a controlled benchmark demonstrating how frequency-sensitive scoring can reach 100 without improving actual professional evidence. **Do not submit its output as a resume.**

## Benchmark evaluation

Read `benchmarks/CALIBRATION_REPORT.md` for seven-job score tables, source URLs, limitations and repeatable comparisons. Use `python benchmarks/compare_all.py --resume /path/to/private-resume.txt`. The user resume is not distributed with this package. The plugin is still skills-only in ChatGPT until a separately deployed, authenticated HTTPS MCP server is connected.
