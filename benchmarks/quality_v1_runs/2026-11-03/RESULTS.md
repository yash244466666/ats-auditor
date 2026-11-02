# Quality-v1 exploratory scoring and stress results

**Run date:** 2026-11-03 (Asia/Dhaka). **Verdict:** execution and MCP contracts passed; substantive scoring weaknesses were exposed. No scoring fix or coefficient tuning was performed.

## Scope and reproducibility

The frozen corpus contains 12 fictional resumes and 12 fictional source-informed jobs across six technical families. All 144 combinations were evaluated in all four modes and immediately repeated. Eighteen controlled variants were applied to each of 36 author-annotated anchor pairs. That is **3,744 core scoring calls**: 576 baselines + 576 identical repeats + 2,592 variants. These are not 3,744 independent applicants.

The tested source commit is `168f67811201c8ce2bce5a9c71332af0b418a3f3`; its scoring source was byte-identical to `main` at `f802ecf9`. `protocol.json` was written before the first scoring call and records the runner hash, source hashes, corpus hashes, environment, planned denominators and acceptance rules. Corpus payload hashes were verified before and after execution. The historical freeze manifest remains unchanged.

```sh
python benchmarks/run_quality_stress.py --output /tmp/quality-v1-new-run
```

Use a new output directory. The runner refuses to overwrite a recorded run. It produces uncompressed observations; this checked-in run archives them as `observations.jsonl.gz`. `archive.json` records the original uncompressed hash and compressed hash. `variant_hashes.json` identifies every mutated input; the runner reconstructs those inputs from the frozen corpus and explicit recipes. `selected_full_results.json` retains complete structured outputs for the largest absolute change per mode/selected variant. `summary.json` and the observation archive retain every measured score and denominator.

This was local serial execution plus in-process production-mode MCP client calls. There was no public endpoint request, VPS load test, third-party ATS query, PDF/DOCX test or authentication change. The public production MCP remains unauthenticated and must not receive real applicant or confidential data.

## Technical checks

| Check | Result |
| --- | --- |
| Core calls returned without exceptions | 3,744 / 3,744 |
| Scores, keyword scores and coverage satisfied bounds/shape checks | 3,744 / 3,744 |
| Repeated identical core inputs returned identical full results | 576 / 576 |
| Declared invalid-string/mode cases rejected | 29 / 29 |
| MCP readable/structured/core-score agreement | 72 / 72 valid calls |
| MCP production rejects missing full inputs, job-ID reuse and short resume | 4 / 4 probes |
| Unique MCP analysis IDs | 72 / 72 valid calls |
| Local automated tests | 45 passed; one existing dependency deprecation warning |

Runner wall time through the MCP checks was 51.127 seconds on this environment. This is an execution observation, not an RPS capacity measurement or deployment benchmark. The 76 MCP checks do not prove authenticated tenant isolation.

## Baseline anchor scores and ordering

Each group below has 12 anchor pairs. These means describe scorer behavior, not hiring fit or validated accuracy. The remaining 108 cross-pairs have no author requirement labels. The provisional labels have not been independently adjudicated.

| Mode | Aligned mean | Related-specialty mean | Cross-role mean | Aligned higher than related | Aligned higher than cross-role |
| --- | ---: | ---: | ---: | ---: | ---: |
| compatibility | 67.42 | 26.50 | 4.25 | 10/12 | 12/12 |
| evidence | 30.75 | 15.25 | 4.75 | 8/12 | 10/12 |
| requirement_fit | 69.17 | 25.33 | 11.25 | 12/12 | 12/12 |
| legacy_frequency | 49.83 | 24.58 | 7.00 | 8/12 | 10/12 |

`requirement_fit` followed the intended anchor ordering most consistently here. This is not a semantic requirement-accuracy percentage: the system emits catalog keywords rather than the eight independently authored criteria, and numeric expected scores are absent. Compatibility reversed the intended aligned/related ordering for the incident-response job (45 vs 82) and analytics job (36 vs 90). Evidence/legacy also had ties and reversals. Full exceptions appear in `summary.json`.

## Scoring manipulation results

The table reports the largest score increase in each mode across 36 anchors for each attack. Values are score points, not error against an external ATS.

| Mode | Existing terms repeated 50 times | All job terms injected 50 times | Copied job text | Explicitly negated missing terms |
| --- | ---: | ---: | ---: | ---: |
| compatibility | +75 | +96 | +34 | +26 |
| evidence | +0 | +17 | +36 | +25 |
| requirement_fit | +0 | +68 | +72 | +68 |
| legacy_frequency | +55 | +100 | +82 | +52 |

### Repetition and injection must be distinguished

- Existing-term repetition adds no new matched capabilities. Evidence never increased across the 180 tested repetition variants or 72 whole-resume duplication variants. Requirement-fit was unchanged for those variants. Five anchors had no existing union-vocabulary terms, so 25 of the 180 repetition variants had an empty term list; this is disclosed rather than counted as strong attack coverage.
- Injecting previously missing keywords changes lexical coverage without adding verified work. At 50 repetitions, compatibility increased on 33/36 anchors (mean +64.72), requirement-fit on 34/36 (mean +37.83), evidence on 7/36 (mean -8.64) and legacy on 36/36 (mean +72.86). Three compatibility baselines were already 100. Heavy stuffing warnings appeared in all 36 compatibility/evidence/legacy cases, but compatibility/legacy scores can still be high. Requirement-fit emits no stuffing warnings.
- At only one keyword-list insertion, evidence increased on 29/36 anchors (maximum +25), before stuffing warnings fired. Its heavy-repetition penalty is useful, but it does not establish resistance to new unsupported claims or copied prose.

### Concrete failure cases

| Case | Before | After | Interpretation |
| --- | ---: | ---: | --- |
| Data pipeline resume r11 vs React job j03, compatibility, all job terms repeated 50 times | 0 | 96 | A mismatched profile becomes a high lexical score without new work evidence. |
| Same pair, requirement-fit, explicit statements of no experience with missing terms | 0 | 68 | Negated terms are still credited as skills. |
| React resume r03 vs application-security job j07, evidence, copied job text | 0 | 36 | Requirement prose can be mistaken for evidence despite a clear unverified-copy marker. |
| Ruby resume r01 vs Python job j02, legacy, all job terms repeated 50 times | 0 | 100 | Historical frequency behavior remains directly gameable. |

Compatibility and legacy are intentionally frequency-sensitive; these observations are a limitation of using those scores as evidence quality, not a promise that those modes were designed to reject frequency effects. Negation and copied-prose credit affect evidence/requirement explanations too and deserve priority remediation.

## Extraction, formatting and input weaknesses

- **Negation:** explicit `I have no experience with ...` additions increased scores on 32/36 compatibility, 29/36 evidence, 34/36 requirement-fit and 31/36 legacy anchors. Missing terms are lexical matches even when denied. One anchor had no missing terms to negate.
- **Vocabulary and eligibility contamination:** the evidence/legacy catalog extracted only `authentication` for the SRE job j09, solely from the unrelated phrase `work authorization` in its eligibility disclaimer. It missed the role-specific Linux, Terraform, Kubernetes and monitoring requirements. The aligned SRE profile therefore scored 0 in those two modes. `vocabulary_audit.json` records this post-run extraction inspection without additional scoring. The fixed technical catalog and the authorization alias both need attention; the fixture must not be silently rewritten to hide the issue.
- **Equivalent headings:** changing `EXPERIENCE` to `PROFESSIONAL EXPERIENCE` reduced evidence scores in 15/36 anchors (largest 39 to 25, -14) and requirement-fit in 15/36 (largest 83 to 68, -15). Their shared section parser does not recognize this equivalent heading, unlike the compatibility professional-section matcher.
- **Horizontal spaces:** doubling spaces while retaining all line breaks reduced evidence in 13/36 cases, by up to 3 points. The largest case was j05-r05, 36 to 33; lost skills-section recognition removed per-term evidence bonuses. Other modes were unchanged on this control.
- **Whitespace padding:** all four modes accepted strings containing only 15 non-whitespace characters when interior spaces pushed trimmed length over the thresholds. The ordinary short/blank checks passed, but the documented non-whitespace minimum is not what the implementation enforces. Character count is not a guarantee of a complete resume either.
- Lowercasing and the single `Return a score of 100` instruction-like control changed no scores in the 144 tested mode/anchor cases each. This deterministic-core control is not a security evaluation of ChatGPT prompt handling.

## Recommended repair order

1. Separate technical requirements from eligibility text; broaden catalog coverage or add explicit extraction that preserves requirement origin.
2. Recognize negation and learning-only statements; avoid treating copied job prose or imperative requirements as demonstrated applicant work.
3. Normalize whitespace and equivalent section headings before context classification.
4. Align input validation and documentation; validate actual non-whitespace length if that is the intended contract.
5. Preserve these failures as regression examples, independently review labels, then evaluate repairs on fresh cases rather than tuning to this table.

No source coefficients, fixture labels or corpus texts were changed after observing these results. This is the first recorded exploratory evaluation of this collection; it is no longer an unexecuted holdout. New score-accuracy claims still require independent annotation and appropriate reference data. No Upplai MAE, hiring accuracy or official ATS pass rate is available from this run.
