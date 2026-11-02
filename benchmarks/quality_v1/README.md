# Quality-v1 evaluation candidate corpus

Created 2026-11-02 (Asia/Dhaka), against repository baseline `f802ecf9`.

**Ready for exploratory scoring/stress tests after structural checks. Not independently validated gold data.**
**Evaluated 2026-11-03:** the [first local stress run](../quality_v1_runs/2026-11-03/RESULTS.md) recorded 3,744 core scoring calls, 76 in-process MCP checks and scoring weaknesses. The frozen payloads were preserved. This collection is now observed evaluation data, not an unexecuted holdout; no scoring coefficients were tuned during the run.

The corpus was authored and its requirement evidence annotated before running ATS Auditor on it. No new-corpus scoring or external ATS queries were performed during collection. The source and label author had access to the existing implementation, so this is not a blind, independent-author evaluation.

## Contents and use

- `resumes.json`: 12 original fictional resumes, 340–358 words each, two per technical role family. Includes summary, skills, work history, projects, education and explicit limitations. Histories and qualifications are invented fixtures, not real applicants or revisions of the owner's resume. Contacts use reserved `example.test` addresses.
- `jobs.json`: 12 self-contained **fictional job descriptions**, 198–213 words each. Each has six required criteria, two preferred criteria, responsibilities and working-context notes. These are deliberately authored test roles informed by public role profiles, **not original employer postings, active vacancies or complete copies of source pages**. Specific stack choices and conditions are fixture-defined; source employers must not be attributed those requirements.
- `sources.json`: 12 successfully retrieved primary role-profile pages from GitLab and the UK Government Digital and Data Profession, with resolved URLs, retrieval date, content hashes, brief role facts and attribution/license metadata. Original pages are not redistributed. A successful retrieval does not establish vacancy availability.
- `labels.json`: 36 anchor pairs and 288 requirement-level author annotations. Each job has an aligned, related-specialty and cross-role comparison. The remaining 108 of the 144 possible cross-pairs are **unlabelled**, not automatically negative.
- `manifest.json`: payload SHA-256 hashes and the historical pre-scoring freeze state. Later evaluation runs belong in separate run records; do not rewrite this historical fact as though it described perpetual holdout status.

Families: backend, frontend, fullstack, application/incident security, infrastructure/reliability, and data/analytics engineering. Related-specialty pairs intentionally include hard negatives: two resumes sharing a broad family do not necessarily share requirements. Coverage is technical and English-only, not representative of all jobs, locales or candidate populations.

Validate from the repository root:

```sh
python benchmarks/validate_quality_corpus.py
pytest -q tests/test_quality_corpus.py
```

The validator never imports or executes the scoring engine. It checks IDs, duplicate/near-duplicate text, section completeness, reserved contacts, career periods, source metadata, requirements, exact evidence quotes and their declared sections, label coverage and frozen hashes. These checks cannot prove semantic label correctness, realistic applicant distributions or absence of every possible privacy issue.

## Annotation contract

| Status | Meaning |
| --- | --- |
| `contextual` | Explicit work or project examples support the full criterion. Multiple quotes may be needed. |
| `partial` | The quoted evidence supports some facets, but not the full compound criterion. |
| `learning_only` | The resume explicitly limits the subject to learning; delivered implementation is not evidenced. |
| `not_evidenced` | The supplied text does not adequately establish the criterion; this is not proof the person lacks the skill. |

Labels describe resume evidence, not verified competence. Required and preferred criteria stay separate. There are no numeric target scores: `expected_score` is null. Location, work authorization and compensation are unspecified, so no eligibility result may be inferred. Learning-only labels and scope notes are useful seeds for subsequent negation tests, not evidence that the engine already understands negation.

Current annotations: 98 contextual, 9 partial, 13 learning-only and 168 not-evidenced. Every evidence quote was checked against the referenced resume. An author semantic pass downgraded compound criteria where quotes supported only part of the requirement. **Independent subject-matter review and adjudication remain pending.** No inter-rater agreement, external reference accuracy or hiring validity has been measured.

## Evaluation discipline

1. Review these labels independently without looking at model scores; record proposed corrections and rationale in a new version/review record.
2. Preserve the frozen inputs and run metadata before evaluating. Report modes separately and keep annotations outside model input.
3. Run baseline, then derive stuffing, duplication, case/alias and malformed-input variants. Store variants separately with parent ID and transformation details; do not describe variants as new independent applicants.
4. Use the 36 annotated anchors for requirement/evidence checks. A numeric score ordering is a hypothesis to investigate, not an independently labeled truth.
5. Once these cases influence scorer tuning, treat them as development data and acquire a fresh prospectively frozen evaluation set. Repeated perturbations and 144 cross-pairs do not increase the number of independent resumes beyond 12.

Do not use this corpus to calculate Upplai MAE: no corresponding observed reference scores exist. Do not combine the older 4.67-point calibration MAE with this new collection. Real-world accuracy still requires consented/de-identified data, independent annotation, multiple source organizations and a protected evaluation process.

## Licensing and attribution

The scoring code, original fictional resume text, annotations and validator remain under the repository MIT license. The job fixture adaptations carry the per-record license in `jobs.json`:

- GitLab-informed job descriptions: **CC BY-SA 4.0**, attributed to GitLab and ATS Auditor contributors, with fictional additions and rewriting identified. GitLab's [handbook reuse statement](https://handbook.gitlab.com/handbook/about/handbook-usage/) supplies the source license; [license terms](https://creativecommons.org/licenses/by-sa/4.0/). No GitLab endorsement is implied.
- Government-informed job descriptions: contain public-sector information licensed under the **Open Government Licence v3.0**, attributed to the UK Government Digital and Data Profession. Rewritten and supplemented with fictional conditions; [license terms](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). No government endorsement is implied.

The per-record data licenses are exceptions to the root code license. Preserve attribution and notices when redistributing fixtures. Source URLs and licenses remain metadata outside scored text. No real resumes, private employer descriptions or public-endpoint requests were involved in collection.
