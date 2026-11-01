# Upplai ATS tool: black-box behavioral analysis and independent reconstruction

## Scope and methodological limits

This is a **behavioral study**, not access to Upplai's internal code or infrastructure. We inspected the publicly exposed tool schema, used authorized input/output interactions, and read the vendor's public documentation. We did **not** extract protected server code, credentials, system prompts, proprietary data, or bypass access controls. The original platform and the independent project remain distinct.

The connected tool exposes `get_resume_ats_score(resume_text?, job_description?, job_description_id?)`. First use expects full resume and job description. Updating a resume can refer to prior `job_description_id`; analyzing a new job can reuse the previous resume. Results include `overall_score`, an opaque `job_description_id`, and keyword entries with `keyword`, `present`, `importance`, `score`. These are **observed interface details** rather than evidence of implementation internals.

## Controlled observations

| Input variant | Score | Keywords matched | Notes |
|---|---:|---:|---|
| Original general software engineer resume vs Truey JD | 23/100 | 6/20 | Many technology terms absent |
| First tailored version | 33/100 | 8/20 | Added TypeScript and context |
| Expanded truthful skills inventory | 55/100 | 20/20 | Keyword coverage achieved, still not 100 |
| Edited company bullets while retaining broad skills | 53/100 | 20/20 | More prose can actually decrease score |
| Contextual capability descriptions | 65/100 | 20/20 | Added per-technology action sentences |
| **Experimental repeated target keyword block** | **86/100** | **20/20** | Most individual keyword scores reached 100; AI stayed 38 |
| **Experimental repeated keyword block + explicit AI repetitions** | **100/100** | **20/20** | All individual keyword scores reached 100 |

The last two inputs were artificial **stress tests**, not documents suitable for job applications. They were not saved to the user's resume. They establish score susceptibility to repetition for this tested job description only.

### Keyword importance and aggregate score

- The Truey job returned 20 recognized keywords. AI was labeled **very high importance**; the others were **low importance**.
- The overall score cannot be a simple *binary keyword coverage percentage*. The 20/20 result still scored 55–65.
- The overall score also cannot be an ordinary unweighted mean of displayed keyword scores. On a 65-point run, the unweighted keyword mean was ~70.8.
- An **importance-weighted mean** is consistent with the observations, with the very-high AI term plausibly carrying around 5–7 times the weight of a low-importance term. This is an *approximation*, not a proven formula; rounding, saturation, scaling, document-level features and hidden penalties may also contribute.
- Increasing keyword frequency materially increased displayed per-keyword scores, often to 100. The tool is therefore not a trustworthy sole measure of real job fit.

### Other learned behavior

- The connected tool rejected a short synthetic `resume_text` input with a message requiring the **full resume text**. This suggests validation of input completeness, but the exact threshold is unknown.
- Raw text-only inputs mean the plugin's actual output cannot demonstrate page layout compatibility, despite Upplai's broader product claiming layout checks for uploaded PDF/DOCX.
- Third-party scores are not guaranteed stable across tool versions or job postings. We did not establish statistical repeatability across hundreds of samples.

## Vendor public statements

The vendor says its resume checker provides ATS and recruiter-style assessments, detects missing keywords and formatting issues, and distinguishes keyword listing from contextual use. See:

- https://www.uppl.ai/resume-checker
- https://www.uppl.ai/

These claims describe a broader product than the limited connected `get_resume_ats_score` tool surface.

## Independent implementation

The package in this archive implements:

- Deterministic, inspectable keyword extraction using an extensible software-engineering catalog.
- Matched/missing keywords, importance, frequency scoring, and 0–100 weighted aggregate.
- `compatibility` mode: deliberate frequency sensitivity, **not exact Upplai parity**.
- `evidence` mode: looks for verbs, quantified outcomes, and work-context mentions, with keyword stuffing warnings.
- Stateful request IDs, updated-resume reuse, and new-job reuse per explicit session ID.
- HTTP API and ChatGPT-compatible MCP adapter source.
- Unit and integration tests for input contract, scoring, context detection, state isolation, and API.

### What cannot be recovered from black-box outputs alone

The vendor's exact model weights, keyword extraction rules, normalization, penalties, thresholds, corpus, prompts, embeddings, data preprocessing, and production source code. Many distinct algorithms produce identical outputs for a small experimental set; inferential claims should stay appropriately limited.

### How to improve accuracy responsibly

1. Build a consented, anonymized evaluation corpus of complete resumes and job descriptions across job families.
2. Vary one factor at a time (term count, placement, exact vs synonym match, context, resume length, section, metrics).
3. Repeat identical queries to measure determinism before fitting weights.
4. Quantify error using mean absolute error by term and by overall score, not just best-case results.
5. Use a train/holdout split to avoid overfitting to the Truey JD.
6. Compare own `compatibility` to vendor behavior, then prioritize `evidence` mode for actual resume decisions.

**Important:** A 100/100 tool score is not an offer predictor and should not be achieved by making false work claims or stuffing unreadable keyword blocks into an application.
