# Phrase extraction and evidence-guard results

Run date: **2026-11-03 (Asia/Dhaka)**. Frozen scoring/evaluation source: [`f3731c066271052f74f5ac1a4a4dd79acc65b45d`](https://github.com/yash244466666/ats-auditor/commit/f3731c066271052f74f5ac1a4a4dd79acc65b45d). This is an observed-benchmark comparison and known fictional regression evaluation, not independent real-world hiring accuracy.

## Extraction: a modest improvement with substantial remaining gaps

The official public SkillSpan test split contains **3,569 sentence records**, **65 within-split document keys**, and **2,265 skill/knowledge union spans**. The new uncapped extractor combines the existing vocabulary, six infrastructure concepts, a training-only 117-phrase lexicon, overlap pruning and explicit-negative job filtering. Production scoring additionally applies keyword caps and weights. Predictions are untyped; partial spans receive no exact-span credit.

| Method | Correct spans | Extra spans | Missed spans | Precision | Recall | Exact-span F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Recorded requirement-fit catalog baseline | 251 | 174 | 2,014 | 59.06% | 11.08% | 18.66% |
| New phrase extractor | 332 | 188 | 1,933 | 63.85% | 14.66% | 23.84% |

This is a **5.18 percentage-point F1 increase**, with 81 more exact matches and 14 more unmatched predictions. It does not mean 23.84% overall ATS accuracy. The new method still misses most labeled phrases. Skill-category recall is 41/1,091 (3.76%); knowledge recall is 291/1,174 (24.79%), using the dataset's categories. Full semantic evidence understanding remains unsolved.

The unique-sentence diagnostic excludes test sentences seen in train/dev and later duplicates within test: 2,404 sentence records, 65 document keys and 2,035 union spans. New results are TP 242, FP 176, FN 1,793; precision 57.89%, recall 11.89%, F1 **19.73%**, versus the prior diagnostic F1 **16.21%**. These are sentence-overlap diagnostics, not a document-disjoint holdout or the official score.

Per-source F1 is 33.21% on `tech` and 9.46% on `house`. Development F1 was 19.51% versus the recorded 15.91% baseline, on 3,174 sentences. A narrow technical dictionary, learned phrase recurrence, token/phrase boundaries, unseen paraphrases and annotation/task differences all limit generalization. Gains cannot be attributed to the lexicon alone. One orphan-I test transition is counted and treated as a span start; original data/splits remain unchanged.

Provenance and all counts: [protocol](runs/phrase-test-2026-11-03/protocol.json), [results](runs/phrase-test-2026-11-03/results.json). The training builder never reads dev/test labels. However, earlier test results informed the development direction, so this is **not a new untouched holdout**. The [initial baseline](RESULTS.md) remains immutable. SkillSpan attribution and its separate [CC BY 4.0 data notice](../../src/ats_auditor/data/SKILLSPAN_NOTICE.md) apply; independent code remains MIT.

## Behavioral checks: targeted failures no longer reproduce

The same 36 known fictional quality-v1 anchors were tested against before/after isolated scorer processes, with baseline, explicit-denial, copied-job, duplicate-resume and equivalent-heading variants in all four modes. That is **720 calls per worker, 1,440 total**, with zero exceptions and all observed scores within 0–100. There are 12 underlying fictional resumes and 12 fictional jobs; variants do not increase independent sample size. Labels remain single-author, pending independent review, and are not numeric score targets.

| Mode/check | Pairs with score increase before | After | Largest increase before → after |
| --- | ---: | ---: | ---: |
| Evidence: copied full job | 30/36 | 0/36 | +36 → 0 |
| Evidence: explicit denial of missing terms | 18/36 | 0/36 | +25 → 0 |
| Requirement fit: copied full job | 34/36 | 0/36 | +72 → 0 |
| Requirement fit: explicit denial of missing terms | 27/36 | 0/36 | +61 → 0 |

For both conservative modes, all 36 pairs were unchanged by each tested copy, denial, duplication and equivalent-heading transformation. All **72/72 baseline compatibility/legacy scores** were preserved. Those historical frequency-sensitive modes still gain from lexical copying/injection; their behavior is not evidence quality. This comparison's missing-term recipe uses the current extractor, so its before counts must not be substituted into the older stress report with a different recipe.

The frozen corpus was read from PR #16 without changing its payloads or copying its data into this PR. [Protocol](../evidence_guard_runs/2026-11-03/protocol.json), [summary](../evidence_guard_runs/2026-11-03/summary.json), [complete observation archive](../evidence_guard_runs/2026-11-03/results.json.gz), and [archive checksums](../evidence_guard_runs/2026-11-03/archive.json) retain the tested sources, corpus hashes, recipes and every result. Decompress the archive to recover the complete original `results.json`; gzip is only a storage representation.

## Verification and practical limits

- **91 local tests passed**, including both MCP tools over real in-process client sessions, explanatory text plus structured results, incomplete production-call rejection, fictional scope/copy regressions, training-only construction and cache-safe non-whitespace validation.
- Source compilation, diff checks, provenance/hash checks, score bounds, metric arithmetic and corpus integrity checks passed. A locally built wheel included the phrase data and notice, loaded them through package resources and rejected a denied-skill example.
- Frozen code passed Python **3.11, 3.12, 3.13 and Docker/container-health CI**: [run 41538421604](https://github.com/yash244466666/ats-auditor/actions/runs/41538421604). Docker is unavailable locally; Docker validation ran in GitHub CI. Subsequent records/docs commits must have their own required CI checked separately.
- No external LLM/provider call, public endpoint load test, production deployment or authentication change occurred. The public MCP endpoint remains intentionally unauthenticated and must not receive real/private applicant data.

These English heuristics can miss complex negation, temporal contradictions and short/paraphrased copies, and may discount genuine long wording shared with the job. Self-attested claims still receive partial credit; copying defenses do not verify competence. Input validation and heading invariance are technical contracts, not accuracy measurements. There are no independent numeric fit targets, so fit-score MAE and worst numeric error are unavailable here.

Next validation should use broader independently authored extraction material and a fresh evaluation source, while keeping matched phrases and excluded evidence inspectable. Do not improve the headline by silently rewriting the frozen dataset, fitting to observed test labels, or interpreting these results as employer decisions.
