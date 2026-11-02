# ATS Auditor — open-source resume–job scoring

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Open source:** MIT License; see [LICENSE](LICENSE), [CONTRIBUTING.md](CONTRIBUTING.md), and [SECURITY.md](SECURITY.md).

**Test data:** See the [data-quality audit](docs/DATA_QUALITY_AUDIT.md) and [quality-v1 corpus](benchmarks/quality_v1/README.md): 12 fictional resumes, 12 source-informed fictional job descriptions and 36 requirement-annotated anchor pairs. Labels are author judgments pending independent review, not ATS ground truth. The adapted job fixtures carry separately documented CC BY-SA 4.0 / Open Government Licence notices; the scoring code remains MIT. Validate without scoring using `python benchmarks/validate_quality_corpus.py`.

**Status:** v0.4.0 developer preview. This project is independently developed and is not affiliated with, endorsed by, or a copy of Upplai. Its estimated scores are heuristic and do not represent actual employer ATS decisions or predict hiring outcomes. The benchmark dataset is small and includes calibration cases; reported fit must not be mistaken for external validation.

**Current security limitation:** The production MCP endpoint is currently public **without authentication**; authentication is deferred. Do **not** submit real resumes, private job descriptions or other sensitive personal data until authorization, rate limits and tenant isolation are implemented. Use fictional test data. See [SECURITY.md](SECURITY.md).

## GitHub and VPS release automation

See [verified status](docs/PROJECT_STATUS.md) and [VPS deployment](deploy/README.md) for the `main` / `dev` pipelines, SSH deployment gate, Caddy TLS and GitHub secrets. Production is deployed at `https://atsmcp.yashcodes.com/mcp` (Streamable HTTP). Production is stateless: send **both** the full resume and job description with every call. The endpoint remains **public and unauthenticated**; user authentication is planned for a later milestone.

**Verified runtime (2026-11-02):** The Python scoring engine, HTTP API and native MCP adapter are implemented; CI runs Python 3.11–3.13 tests, creates the MCP server, builds and starts the Docker image, and checks `/health`. [CI](https://github.com/yash244466666/ats-auditor/actions/runs/41349223958) and [production deployment](https://github.com/yash244466666/ats-auditor/actions/runs/41349261322) both passed for commit `d74350bf`. Live ChatGPT connector calls to both MCP tools returned populated structured scores and text results after [PR #11](https://github.com/yash244466666/ats-auditor/pull/11). Scores remain experimental heuristics, not official ATS outputs.

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

The MCP SDK serves Streamable HTTP on port 8000 inside the container, with Caddy publishing production at `https://atsmcp.yashcodes.com/mcp`. The native MCP tools have been called successfully from ChatGPT with fictional test data.

The MCP server is already deployed and its two tools were successfully invoked by a ChatGPT-connected MCP integration. For additional connections, ChatGPT's plugin/MCP setup depends on account and workspace support. Authentication has **not** been implemented; do not test with sensitive applicant data. See https://developers.openai.com/plugins/build/mcp-server and https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt.

The bundled MCP tool names are:

- `get_resume_ats_score` — compatible 3-primary-parameter workflow, optional `session_id`, `scoring_mode`.
- `compare_resume_quality` — evidence-based assessment that flags stuffing.

ChatGPT cannot connect to `localhost` on the VPS. The published URL is `https://atsmcp.yashcodes.com/mcp`, and tools are already available through a connected ChatGPT MCP integration in the verified conversation. The bundled **private skills plugin** and the **hosted MCP server connection** are separate: installing a skills-only bundle does not itself activate remote tool access.

## Scoring modes

**Compatibility (default)**: Expanded dictionary of requirements, missing keyword penalties, job-description frequency and title salience, tuned against observed third-party results for seven technical jobs. On 12 fictional-resume/job comparisons, development/inspected-validation MAE 4.67 points, with a worst observed difference of 22 points. This is NOT blind validation or exact Upplai parity.

**Legacy frequency** (`legacy_frequency`): Prior v0.2 count-based heuristic, preserved for backwards-compatible experiments.

**Evidence**: Rewards contextual project achievements, quantified results, and verified technical usage; repeated keywords alone receive limited additional credit and can incur a penalty. This mode is more suitable for resume optimization.

Neither is an actual employer ATS decision. Both work on extracted text, not on actual PDF/DOCX layout. Production layout analysis would need a separate document-parsing stage.

## Privacy and security

- The CLI and core do not send resumes to any external service or model.
- The HTTP and MCP servers are self-hosted. Caller-provided resume/job text is processed by the VPS deployment; do not claim end-to-end privacy without authentication and a review of logging and retention.
- The **local-development** service may cache resume/job text by `session_id` for up to one hour. **Production MCP** is stateless and creates a fresh isolated service instance for each call; both complete input texts are required each time. Stateless operation is not authentication.
- **The public production MCP route is currently unauthenticated. Do not send real applicant data until OAuth 2.1 or a verified compatible alternative, per-user authorization, tenant isolation, rate limiting and safe audit controls are deployed.** `session_id` is not authentication.
- HTTP API supports a simple development `ATS_API_KEY` environment variable; production MCP should instead use robust OAuth or mTLS controls suited to the deployment.
- Example data is fictional. No user's personal resume is bundled.

## Limitations compared with Upplai

- Internal weights, model prompts, embedding methods, code, training data, and score normalization are not accessible, so exact output parity cannot be guaranteed.
- Only selected behavior is reverse engineered using black-box observations and public claims. A full benchmarking effort requires a labeled evaluation set, repeatability tests, rate-limit awareness, and comparisons across multiple job families.
- This replica does not yet parse binary PDF or DOCX, implement recruiter scoring, edit resumes, integrate with Google Drive, or provide a custom in-chat UI. Those are separate phases.
- The MCP adapter has passed in-process MCP client-call regression tests and real ChatGPT tool calls with fictional text. Remote deployment success and these smoke tests do not establish scoring accuracy, privacy safeguards or production readiness for sensitive data.

For reproducible multi-resume observations, see `benchmarks/INDEPENDENT_VALIDATION.md`. For inferred scoring behavior, see `docs/REVERSE_ENGINEERING.md`.

## Reproduce the 100% failure mode (synthetic data only)

```bash
PYTHONPATH=src python examples/stress_test.py
```

This is a controlled benchmark demonstrating how frequency-sensitive scoring can reach 100 without improving actual professional evidence. **Do not submit its output as a resume.**

## Benchmark evaluation

Read `benchmarks/CALIBRATION_REPORT.md` for seven-job score tables, source URLs, limitations and repeatable comparisons. Use `python benchmarks/compare_all.py --resume /path/to/private-resume.txt`. The user resume is not distributed with this package. The endpoint is already connected and both MCP tools have returned scores in a ChatGPT conversation; additional installations or account connections remain separate steps.
