# Phrase extraction and evidence guards

Review-branch change, 2026-11-03 (Asia/Dhaka). Production has not been updated by this work. The endpoint remains public and unauthenticated; use fictional data for public tests.

[Recorded post-change results and limitations](../benchmarks/public_skillspan/IMPROVEMENTS_2026-11-03.md): exact-span F1 18.66% → 23.84%; no gains from the tested copies/denials in 36 known fictional pairs per conservative mode. Recall remains only 14.66%; no overall ATS accuracy is established.

## What changes

Evidence and requirement-fit scoring now share requirement extraction and evidence classification. Compatibility keeps its existing empirical formula, vocabulary and frequency behavior; legacy frequency keeps its historical matching/scoring path. They are not aliases of the more conservative modes.

The extractor merges existing aliases, six infrastructure concepts (Linux, Prometheus, Grafana, Bash, service-level objectives and site-reliability engineering), and 117 training-derived phrases. It retains requirement origins and character offsets, avoids some nested fragments, and filters explicit negative/optional job mentions and work-authorization phrases. It is not a complete semantic requirement or eligibility parser. Terms absent from its vocabulary and paraphrases can still be missed.

## Training-derived phrase data

`src/ats_auditor/data/skillspan_phrases.json` is generated from the pinned **training split only**, using `benchmarks/build_skillspan_lexicon.py`. Entries must occur as annotated spans in at least two distinct source/document keys and achieve at least 0.8 exact-span precision among training occurrences; normalized phrases are limited to 12 tokens. Placeholders, malformed punctuation and control-character artifacts are excluded. These are fixed training-only rules, not thresholds fitted to the public test results.

The result is a small local trie, not a downloaded neural model. There are no new runtime dependencies or remote calls. The lexicon is packaged in wheels/containers with its [CC BY 4.0 attribution notice](../src/ats_auditor/data/SKILLSPAN_NOTICE.md); the independent Python code remains MIT. Counts and provenance are embedded in the artifact. No original job sentences or applicant resumes are redistributed.

To reproduce the artifact, first populate the pinned cache using the [public benchmark](../benchmarks/public_skillspan/README.md), then:

```sh
python benchmarks/build_skillspan_lexicon.py --output /tmp/skillspan-phrases-new.json
cmp src/ats_auditor/data/skillspan_phrases.json /tmp/skillspan-phrases-new.json
```

The builder refuses to overwrite an existing artifact. Development/test labels are not used by the builder. Once an observed test release informs our development choices, it is no longer an untouched holdout, even when the artifact itself uses training labels only.

## Evidence classifications

| Status | Evidence score | Requirement-fit credit | Meaning |
| --- | --- | --- | --- |
| Contextual | Existing action/metric formula, starting at 40 | 0.85 | An action-based example appears in the supplied text; not independent employment verification. |
| Self-attested | 25 | 0.68 | A positive mention without an action-based example; claims alone still receive partial credit. |
| Learning only | 10 | 0.15 | Studying, tutorials or learning are explicit; delivered work is not established. |
| Excluded or absent | 0 | 0 | Explicit denial, detected job overlap, requirement prose, or no matching mention. |

English negation checks preceding and following cues within bounded clauses, handles comma-separated lists and common pseudo-negation such as “not only”, and resets scope at contrasts. Separate positive examples are retained when a denied or copied mention also occurs. Action/metric evidence is deduplicated across repeated text and scoped to avoid borrowing context from a contrasting skill claim. Equivalent professional-experience/skills headings and horizontal whitespace are normalized.

Job-overlap checks normalize words, find shared eight-word shingles and exclude merged shared runs of at least 12 words. Character offsets let a separate genuine example survive. Explicit job-copy headings are also excluded. Short generic skill lists are not treated as copies. Human-readable reports and structured results explain excluded and learning-only mentions.

These rules do not establish plagiarism, dishonesty or lack of ability. Genuine descriptions can share long wording with a job, and short copies, paraphrases, unusual grammar, temporal contradictions and languages other than English may evade detection. Presence is not proof. Avoid recommending false claims to raise scores.

Validation now counts actual non-whitespace input characters in the dispatcher and service before caching incoming text. Whitespace padding no longer bypasses documented minimums. This affects malformed inputs across modes without retuning the compatibility formula.

## Verification and evaluation

Fictional tests cover explicit pre/post denials, pseudo-negation, contrasts, mixed learning, exact copies, separate genuine evidence, heading/spacing equivalence, training-phrase extraction, eligibility contamination, padding/cache safety, trie offsets and train-only construction. Real in-process MCP client calls exercise both tools, text/structured output, exclusions and stateless rejection of incomplete production calls.

The development extraction check improved exact-span union F1 from 15.91% in the recorded catalog baseline to 19.51% with the new uncapped extractor, on 3,174 development sentences. This is a development result with low remaining recall, not an untouched or representative hiring-accuracy estimate. The final observed-test run is recorded separately after source freeze.

Reproduce extraction on a new output directory:

```sh
python benchmarks/compare_phrase_extraction.py --split dev --output /tmp/phrases-dev-new
python benchmarks/compare_phrase_extraction.py --split test --output /tmp/phrases-test-new
```

These compare the new uncapped runtime extractor with the immutable prior catalog baseline; production scoring still applies its keyword cap and weights. Exact token spans must match. The new method adds a lexicon, infrastructure terms, overlap pruning and explicit-negative job filtering, so gains cannot be attributed to the lexicon alone. Train/test overlap diagnostics remain separate. No category precision/F1 or universal 0–100 fit truth is invented.

For the previously observed fictional corpus in PR #16, use separate clean checkouts for the old scorer and current scorer:

```sh
python benchmarks/compare_evidence_guards.py \
  --corpus /path/to/quality-v1-checkout/benchmarks/quality_v1 \
  --baseline-source /path/to/old-scorer-checkout/src \
  --output /tmp/evidence-comparison-new
```

The runner checks frozen corpus hashes and declared fictional records, writes the protocol first, executes before/after workers in isolated Python processes, and records every score. It uses 36 anchors, five variants and four modes: 720 calls per worker, 1,440 total. Variants are not independent applicants and author labels are not adjudicated gold. Copied/negated score gains, duplication and heading invariance are behavioral checks; compatibility/legacy baseline preservation is checked separately. The old corpus is supplied rather than duplicated or altered in this PR.

The initial public baseline and its protocol/results remain unchanged. All post-change measurements belong in new run directories with new source hashes. No public endpoint load testing, real applicant processing or production deployment is claimed.
