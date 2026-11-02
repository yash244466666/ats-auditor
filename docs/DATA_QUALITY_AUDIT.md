# ATS Auditor test-data quality audit

Date: 2026-11-02 (Asia/Dhaka). Baseline inspected: `f802ecf9`. Scope: test-data suitability for the planned scoring and anti-stuffing stress tests. No new scoring-accuracy claim is made.

## Decision

**Existing data is useful for regression checks but insufficient for broad scoring validation.** The new [quality-v1 corpus](../benchmarks/quality_v1/README.md) expands exploratory coverage and makes expected requirement evidence inspectable. It is synthetic, single-author data pending independent review, so it does not resolve real-world generalization or provide official ATS ground truth.

## Existing-data inventory

Reproduce counts with `python benchmarks/validate_quality_corpus.py`; the tool parses fixtures without executing the scoring engine.

| Source | Records | Text length | Intended/actual status |
| --- | ---: | --- | --- |
| `benchmarks/independent_resumes.py` | 4 resumes | 242–264 words | Rails, frontend, backend, security; used in inspected calibration |
| `benchmarks/jobs.json` | 7 job briefs | 162–223 words | All seven observations eventually inspected/calibrated, despite historical train/holdout tags |
| `benchmarks/independent_results.json` | 12 observed pairs | Four resumes reused | External observations used in inspected calibration; not independent holdout |
| `benchmarks/holdout/synthetic_resumes.json` | 4 resumes | 253–259 words | Additional authored examples; no independent gold labels |
| `benchmarks/holdout/new_public_jobs.json` | 5 job briefs | 106–157 words | Summarized technical roles with links; no observed external scores |
| `examples/synthetic_resume.txt` / `examples/truey_job.txt` | 1 resume / 1 job | 220 / 111 words | Shared demonstration and stuffing-test seed, not new independent validation |

There are zero normalized exact duplicates across the nine fictional resumes above. This does not make them nine representative real applicants. Python authoring files that reproduce the same JSON fixtures are not additional records. The original single-user resume referenced in the seven-job calibration report is private and unavailable in the repository; it is excluded from this inventory and not reconstructed or counted as an available fixture.

## Findings and implications

| Severity | Finding and evidence | Consequence / remediation |
| --- | --- | --- |
| High | `CALIBRATION_REPORT.md` explains that all seven observations were used after inspecting the original holdouts. `independent_comparison_results.json` also discloses inspected calibration. | Directory names and split tags must not be reported as blind validation. Preserve historical data; use a fresh versioned prospective set. |
| High | The additional four-resume/five-job set has no requirement annotations or observed source scores. | It cannot establish reference-score error or requirement extraction correctness. Author explicit evidence labels and obtain independent review. |
| High | Available profiles are fictional and technical, with narrow candidate and job-family diversity. | Repetition of variants/cross-pairs is not new independent data. Add role breadth now; later acquire properly consented/de-identified real-world evaluation data. |
| Medium | Five newer JDs are 106–157-word summaries with URL/title/family metadata, without capture date, source hash or requirement-origin flags. | Cannot reproduce original postings or prove exact-source fidelity. New fixtures identify sources, dates and fictional additions explicitly. |
| Medium | Current stress example uses one job and a 45-fold keyword block. | It detects a narrow failure mode. The new collection supplies multiple families and related/cross-role contrasts for later controlled variants. |
| Medium | Added profiles have uniform section structure and were written by the same author as their labels. | Synthetic/template and author bias remain. Add independent review and future document/format/language diversity before claiming broader performance. |

These findings come from current files and their declared methods, not an independent revalidation of every old external job URL or historical Upplai result. Historical numeric observations are preserved as recorded. No temporal trend is inferred from two small curated releases.

## What was added

- 12 new original fictional resumes (340–358 words), with coherent dated histories, project boundaries and explicit learning-only limitations.
- 12 fictional source-informed job descriptions (198–213 words), across six families with required/preferred requirements separated.
- 12 successfully retrieved primary public role-profile pages from two publisher organizations. Job profiles are references, not verified current vacancies or copied full employer postings. Original pages are not redistributed.
- 36 anchor pairs with 288 author requirement annotations and exact evidence quotes; numeric expected ATS scores are absent.
- A frozen manifest, attribution/license notices, a data-only validator and regression tests for corrupted references/evidence/labels.

Content lengths are completeness checks, not quality scores. Resume dates, record references, quote locations, contact domains, duplicate text and payload hashes were checked programmatically. Semantic annotation was reviewed by the author; no independent adjudication or inter-rater agreement is claimed. The corpus was not scored during this collection, and has not been used to tune coefficients.

## Acceptance and next use

Use this collection for the first exploratory scoring/stuffing run, preserving the frozen inputs and reporting failures. Treat evidence annotations as reviewable expectations. Independent domain review is the remaining gate for calling these gold requirement labels. Realistic population accuracy, external-provider parity, binary document parsing, nontechnical roles, languages beyond English and authenticated tenant behavior remain outside this data's scope.

No production load test or public scoring call was performed. The public MCP remains unauthenticated by owner decision; all future public smoke tests must continue to use fictional data.
