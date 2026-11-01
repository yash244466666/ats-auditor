# ATS Auditor v0.4 — multi-resume validation and reliability report

**Date:** 2026-11-01. **Source of target scores:** live Upplai connector output in this conversation, using full fictional resumes and real-job-derived technical briefs. All supplied people/companies in example resumes are fictional. The job descriptions are reconstructed summaries of public postings rather than verbatim originals. Never infer employment eligibility from these scores.

## Why this release exists

Version 0.3.1 approximated one broad software engineer's Upplai scores with low development error but severely under-scored specialist resumes. The same full fictional Ruby, React, Python/Django and security resumes were then compared against multiple jobs. Negative cross-role pairings were included to avoid indiscriminately boosting scores.

## Observations

See `independent_results.json` and `independent_comparison_results.json` for individual source scores and local estimates. Reproduce with `python benchmarks/compare_independent.py`.

| Resume / target | Upplai | ATS Auditor v0.3.1 lexical | v0.4 after context calibration | v0.4 absolute error |
|---|---:|---:|---:|---:|
| Ruby / Stora Rails | 64 | 36 | 64 | 0 |
| React / Smart Working | 70 | 28 | 78 | 8 |
| Django / Plentific | 94 | 34 | 86 | 8 |
| Security / LiteLLM | 84 | 43 | 80 | 4 |
| React / Stora Rails (negative) | 9 | 5 | 8 | 1 |
| Ruby / Smart Working (negative) | 9 | 0 | 7 | 2 |
| Django / Taktile AI full-stack | 25 | 9 | 24 | 1 |
| Django / BlancVPN | 55 | 38 | 64 | 9 |
| Security / Stora Rails (negative) | 3 | 0 | 3 | 0 |
| React / Taktile AI full-stack | 35 | 8 | 35 | 0 |
| React / Vynca full-stack | 24 | 9 | 23 | 1 |
| Security / Plentific Python backend | 30 | 6 | 8 | **22** |

**Mean absolute error across these 12 pairs:** 19.17 points under v0.3.1's lexical model, **4.67 points** with v0.4. On the seven original single-resume comparisons, v0.4 MAE is **2.86** points versus 3.29 in v0.3.1. These are mixed development and inspected validation results, **not an unbiased estimate on a blind dataset**.

## Model modifications

- Compute the fraction of *distinct job requirements* demonstrated in the resume's professional experience, separately from repeated mentions in skill lists. A restrained second-stage adjustment recognizes concentrated, role-specific professional histories.
- For explicitly full-stack roles listing both frontend and backend technologies, give limited partial-match credit to a candidate who shows practical experience in one complete half of the stack. This is a bounded floor, not additive repetition credit.
- A lexical score floor reflects modest transferable keyword coverage even if the reference frequency model is unusually punitive.
- Report the baseline lexical score, professional context fraction, adjustment and partial-stack floor in the response so the calibration is inspectable.
- Identify low-coverage cases as high uncertainty. This model intentionally does **not** create a special exemption for the security-to-Python-backend outlier; doing so solely to match one Upplai observation would overfit.
- Preserve `requirement_fit` and `evidence` modes separately from `compatibility` (source-approximation). Only compare the compatibility mode numerically with Upplai.

## Reliability checks

- 25 automated unit/integration tests pass in the offline Python environment.
- HTTP scoring contract and production-token behavior tested with FastAPI TestClient.
- `required` job text and resume text validated before mutating server session state; failed changes cannot corrupt a valid cached resume.
- Requirement-fit mode now works through the HTTP route (fixes an earlier response-format error).
- The code depends on no remote ATS or LLM service for local scoring.

## What remains uncertain

1. Upplai uses dynamic keyword selection; our public dictionary cannot reproduce semantic keyword extraction exactly. Upplai may assign different scores or terms to paraphrased job text.
2. The observed 22-point failure on the security-to-Python-backend pairing shows this is **not** a precise clone and may diverge on other transferred-skill scenarios.
3. 12 fictional pairs from four resumes are too few for a robust generalization claim. Broad job-family validation requires many independent, consented, diverse, anonymized resumes with strict untouched test groups.
4. Job location, visa/authorization, salary and seniority are *eligibility checks*, not numerical keyword scores.
5. MCP server transport has not been verified with the official `mcp` Python SDK (not available in the offline build environment), and no authenticated HTTPS deployment exists yet.
6. For a production personal server, enforce TLS, user authentication, rate limiting and tenant isolation; an unprotected MCP endpoint must not accept private resumes.

## Suggested next experiments

Create an untouched sample of 20–50 independent resumes across backend, frontend, full-stack, infrastructure, security, data and nontechnical roles. Pair each with several job descriptions, repeat some Upplai queries for stability, compare per-keyword discrepancies, then calibrate the extractor and weighting on a training split only. Record uncertainty intervals and validate on fresh samples without tuning against them.
