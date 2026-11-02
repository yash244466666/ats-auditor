# SkillSpan: first external extraction baseline

Run: 2026-11-02 UTC. **Finding: the current fixed vocabularies cover only a small part of the annotated skill/knowledge phrases.** This is a measurable extraction limitation, not an overall ATS accuracy estimate.

## Method and provenance

The [published evaluator commit](https://github.com/yash244466666/ats-auditor/commit/21b62d44674769b7fc89485812ba37d7fbded99f) fixes the runner, existing matcher/vocabularies and protocol before evaluation. Full source and dataset SHA-256 values, timestamp and policies are recorded in [protocol.json](runs/verified-baseline-2026-11-02/protocol.json); all counts are in [results.json](runs/verified-baseline-2026-11-02/results.json). The earlier local run used an identical source tree; the published-commit run verifies reproducibility rather than adding independent samples.

The upstream snapshot is `2ccf3de5b5af7a5409b8dd814fb1315dd6e0ae1b`. Attribution: SkillSpan, Zhang, Jensen, Sonniks and Plank, [NAACL 2022](https://aclanthology.org/2022.naacl-main.366/), with CC BY 4.0 data declared by the [author dataset card](https://huggingface.co/datasets/jjzha/skillspan/blob/main/README.md). Source code is separately MIT. Data was cached locally and its hashes verified; corpus text is not redistributed in this PR.

## Official test split

There are **3,569 sentence records**, **65 document keys within the split** and **2,265 gold spans** in the skill/knowledge union. Predictions are uncapped catalog detections, not the full scoring/extraction interface. Exact token boundaries must match. Predicted spans have no skill/knowledge category, so primary metrics use their union.

| Adapter | Correct spans (TP) | Extra spans (FP) | Missed spans (FN) | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Evidence catalog | 144 | 124 | 2121 | 53.73% | 6.36% | 11.37% |
| Compatibility catalog | 225 | 341 | 2040 | 39.75% | 9.93% | 15.90% |
| Requirement-fit catalog | 251 | 174 | 2014 | 59.06% | 11.08% | 18.66% |

The requirement-fit catalog detected 251/2,265 gold spans and made 174 unmatched predictions. Of its matches, 248 were knowledge spans (248/1,174) and three were skill spans (3/1,091). These category names follow the dataset's annotation guidelines. Exact-span scoring penalizes partial phrase matches; space-joining source tokens can also impair dotted or hyphenated aliases. This is a task and representation mismatch to report, not a reason to rename recall as hiring accuracy.

For that same catalog, test F1 is 26.17% on the `tech` source and 7.56% on `house`. Those subsets contain 2,286 and 1,283 sentence records respectively. This limited benchmark is neither a population estimate nor a comparison proving one full scoring mode more accurate than another.

## Data-quality findings and overlap diagnostic

| Split | Sentences | Document keys within split | Duplicate normalized sentence rows | Orphan-I starts |
| --- | ---: | ---: | ---: | ---: |
| Train | 4,800 | 140 | 857 | 0 |
| Development | 3,174 | 58 | 577 | 0 |
| Test | 3,569 | 65 | 909 | 1 |

Cross-split unique normalized sentence intersections: train/development 159; train/test 177; development/test 169. These can include boilerplate and do not establish full-document leakage. No official split was rewritten. The single test orphan-I is explicitly treated as a span start and counted; raw tags remain unchanged.

A separate diagnostic keeps the first unique test sentence absent from both training and development: **2,404 sentences**, still covering 65 document keys, with **2,035 gold union spans**. The requirement-fit catalog gives TP 194, FP 165, FN 1,841; precision 54.04%, recall 9.53%, F1 16.21%. This diagnostic removes repeated sentences, not semantic near-duplicates, and is not an official benchmark score. The full JSON includes all adapters, train/dev results and per-source test counts.

## Verification and remaining work

- 48 local pytest tests passed, including 12 new fictional/offline evaluation checks. Both existing in-process MCP tool-call tests remain in the full suite.
- Compilation and diff whitespace checks passed. The benchmark reads no real applicant resumes and makes no public endpoint or external LLM calls.
- No vocabulary entries, scoring weights, frozen fictional corpus records, SDK bounds, deployment settings or authentication settings were changed. This result does not fix the prior stuffing, negation, copied-text, heading or input-validation weaknesses.
- The two non-permutation arrays in the separate human-ranking dataset remain unresolved; no human ranking accuracy is claimed here.
- GitHub CI and PR state must be checked independently; local results do not claim deployment success.

Next, develop broader phrase extraction on training/development material and preserve traceable requirement origins. Test negation and evidence claims separately using fictional cases. Any subsequent tuning informed by this test baseline makes it observed development evidence; acquire a fresh evaluation source before claiming untouched generalization. No universal ATS score target or hiring truth is supplied by SkillSpan.
