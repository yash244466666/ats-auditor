# Public SkillSpan extraction benchmark

This page describes the **initial baseline** at evaluator commit `21b62d44674769b7fc89485812ba37d7fbded99f`; check out that commit to reproduce its exact catalogs. Later [phrase/evidence changes](../../docs/EXTRACTION_EVIDENCE.md) have a separate comparison runner and records. The historical baseline results remain immutable.

This benchmark evaluates existing ATS Auditor vocabularies against externally authored expert skill/knowledge annotations. It does **not** measure resume fit, employer ATS scores, evidence verification, or hiring outcomes. No new model, runtime dependency, or scoring change is introduced.

[First recorded baseline and limitations](RESULTS.md).

[Post-change results](IMPROVEMENTS_2026-11-03.md) record the subsequent phrase/evidence implementation against frozen source, without overwriting the initial baseline.

## Data and attribution

SkillSpan, by Mike Zhang, Kristian Jensen, Sif Sonniks and Barbara Plank, NAACL 2022: [paper](https://aclanthology.org/2022.naacl-main.366/), [repository](https://github.com/kris927b/SkillSpan), [author dataset card](https://huggingface.co/datasets/jjzha/skillspan/blob/main/README.md).

The repository code license is MIT; the dataset card declares [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). These are distinct notices. Data is fetched locally from pinned commit `2ccf3de5b5af7a5409b8dd814fb1315dd6e0ae1b` and checked against hard-coded SHA-256 values. Do not relicense external data under our root MIT license. No corpus text is committed here; aggregate result files identify the snapshot and attribution.

The public release covers two sources, with 4,800 training, 3,174 development and 3,569 test sentence records. Sentences are nested in documents and may repeat; they are not independent applicants or 11,543 independent jobs. Document keys combine source and idx within each split; IDs restart between splits.

## Reproduce

From the repository root with the normal development environment installed:

```sh
python benchmarks/evaluate_skillspan.py --download --output /tmp/skillspan-new-run
pytest -q tests/test_skillspan_evaluation.py
```

Use a **new output directory** for every run. The default cache is ignored by git at `benchmarks/.cache/skillspan/`; `--cache PATH` overrides it. `--download` permits fetching absent files from the pinned public URLs. Without it, the runner is entirely offline and requires verified cached files. A stale or corrupt cache fails closed and is never silently replaced. Unit tests use fictional text and never download data.

`protocol.json` is written before data loading/scoring; `results.json` is created only after successful evaluation and final source/data hash verification. Failed runs may leave a protocol without results. The protocol identifies source hashes, source revision, data snapshot, metrics and policies. A successful run must contain both files. Results record no document text, contact information or applicant data. No public MCP calls are made.

## Fixed evaluation protocol

1. Three **uncapped catalog-scan adapters** use existing code and aliases: evidence catalog; compatibility catalog (base plus extended vocabulary); requirement-fit catalog excluding its stop terms. They evaluate vocabulary detection, not each mode's full top-N extractor, weights, scoring, requirement priority or evidence logic.
2. Join source tokens with a single space. Use the existing `_occurrences` matcher; keep only token-aligned character matches. Retain nested predictions and deduplicate identical spans. No gold labels influence predictions. Dotted/hyphenated terms split into source tokens may become difficult to match; no detokenization model is added.
3. Convert both BIO streams to token spans with exclusive ends. Preserve skill/knowledge overlaps, but deduplicate identical spans in their union. Treat an orphan `I` after `O` as a new `B`, count it, and leave raw data unchanged. The inspected test file has one such transition; train/dev have none.
4. Primary metrics are **micro exact-span precision, recall and F1 on the official test split**, against the untyped skill/knowledge union. Partial phrase matches receive no exact-span credit. Report skill recall and knowledge recall separately. Predictions do not have category labels, so category precision/F1 are deliberately absent.
5. Report all official splits, per-source test metrics and a separate diagnostic retaining only the first normalized test sentence absent from both training and development. The normalization is casefolded space-joined tokens. This diagnostic removes repeated sentences, not complete documents or semantic near-duplicates; it is not an official alternative test split.
6. Keep the scorer/vocabulary fixed during this first baseline. This is external-author annotation, not a claim of a prospectively blind or contamination-free evaluation. Once test results influence changes, that release is observed development evidence; future generalization needs a fresh evaluation source.

The audit reports within-split repetition and cross-split sentence intersections. Repetition can be boilerplate; it does not alone prove whole-document leakage. Official metrics remain unchanged, and diagnostic denominators are explicit. No confidence interval treating correlated sentences as independent is claimed.

## Acceptance criteria

- Source snapshot and exact data hashes are recorded and verified before/after evaluation.
- Malformed rows, unexpected tags, missing data and stale cache are rejected.
- Span boundaries, aliases, exact-match errors, overlap deduplication, orphan handling, cache failures, protocol order and overwrite protection have fictional regression tests.
- Official and diagnostic results are separate, with TP/FP/FN counts and source/record denominators.
- No coefficients, catalog entries, frozen fictional fixtures, authentication, deployment or public endpoint are changed to improve the numbers.
- Report the baseline even if poor. Extraction F1 must never be relabeled overall ATS accuracy or combined with historical Upplai calibration MAE.

## Other datasets and remaining work

[Vanetik's dataset](https://github.com/NataliaVanetik/vacancy-resume-matching-dataset) has human rankings for 30 resumes across five jobs, but the inspected annotation file contains two non-permutation arrays (reviewer 1, rows 9 and 28). Rank encoding, ties, data rights/privacy and label adjudication must be settled before scoring that task. No real CVs are imported here and no labels are silently repaired.

JobResQA tests synthetic document questions; the current deterministic engine does not expose a general question-answering interface, so no artificial QA accuracy is reported. Djinni provides real profiles/jobs but no independent human match targets for our scorer. Neither is a drop-in numeric ATS score benchmark.

Known stuffing, copied-text, negation and input/heading weaknesses from the prior stress work remain separate remediation work. This benchmark establishes a reproducible extraction baseline first. Production authentication is intentionally deferred; real/private evaluation must stay local or controlled, never on the public unauthenticated MCP endpoint.
