# ATS Auditor v0.3 — Upplai black-box comparison

**Date:** 2026-11-01. **Method:** One fixed, complete, real software engineer resume (held privately) was compared against 7 distinct public-job-derived technical briefs. Additional known Truey comparison was used as a control. Benchmark job briefs paraphrase/publicly reconstruct the role's requirements; they are **not** identical downloadable copies of every original job page.

## Results

| Job | Upplai | ATS Auditor v0.2 legacy | v0.3 calibrated | Absolute error v0.3 |
|---|---:|---:|---:|---:|
| Vynca — Senior Full Stack | 28 | 80 | 29 | 1 |
| Plentific — Senior Backend | 29 | 67 | 22 | 7 |
| Stora — Software Engineer II (Ruby) | 19 | 77 | 17 | 2 |
| Smart Working — Senior Frontend | 21 | 75 | 22 | 1 |
| LiteLLM — Senior Security | 10 | 65 | 3 | 7 |
| Taktile — AI Full Stack | 37 | 79 | 38 | 1 |
| BlancVPN / Yadda — Python Django Backend | 13 | 66 | 17 | 4 |
| **Mean absolute error (seven)** | | **50.29** | **3.29** | |

Additional Truey control from previously confirmed job description: Upplai 68, original ATS Auditor 75, calibrated version 67.

## Principal discoveries

- The third-party response keyword selection is **job-specific and variable**: among the seven jobs it returned between 16 and 55 keywords, including phrases outside the original ATS Auditor's 55-term technology list.
- The third-party keyword presence signal is **not reliably exact-phrase matching**. Some responses marked semantically or partially overlapping phrases as present (e.g. a broader UI term). Do not assume presence flags reveal the private implementation.
- The third-party result is influenced by term frequency, role salience and missing skills. Repetitive synthetic input previously pushed the benchmark score to 100 without stronger evidence.
- ATS Auditor v0.2 was far too generous on diverse job postings because it extracted only a narrow catalog and almost all extracted terms appeared in the technology-rich resume.
- ATS Auditor v0.3 uses a broad, inspectable technical dictionary, includes missing requirements, weights repeated job requirements and role-title terms, and normalizes the resume mention counts relative to job mentions.
- A separate *evidence* score remains unchanged: it measures context, action verbs, project outcomes and possible keyword stuffing, and should not be compared numerically to Upplai.

## Experimental procedure and limitations

1. Source results were obtained using Upplai's public connector tool, with a full resume and a distinct job description per call. See `jobs.json` for technical briefs and job links. Raw personal resume text is deliberately excluded from the plugin package.
2. Five roles were initially earmarked for calibration and two for holdout. After the first version yielded a holdout error of approximately eight points on average, **all seven job observations and the Truey control were inspected and used for a second calibration**. Thus the final 3.29 MAE is a **development-set fit**, NOT an unbiased estimate of generalization error.
3. The coefficients were optimized by deterministic random search and then rounded for the v0.3 release. They are *not* the Upplai source code, and no claims of exact algorithm reproduction are made.
4. Three additional real postings were selected for genuine post-calibration evaluation (EasyLlama, Ascertain, BioRender), but Upplai rejected subsequent calls with a service/usage error directing requests to its website. Do not report unavailable ground-truth scores for those postings.
5. A single user's resume is an insufficient evaluation population. A next meaningful benchmark would cover at least 10–20 different consenting, de-identified resumes, paired with 3–5 job families, independent score repeats and a prospective holdout split. Note the third-party tool's rate limits and privacy requirements.
6. Real recruitment eligibility (location, visa, salary, language) is not the same as keyword compatibility. Several postings tested here are restricted to the US/EU/Pakistan.

## Reproduce

```bash
pip install -e '.[dev]'
pytest -q
python benchmarks/compare_all.py --resume /path/to/private-resume.txt
```

Expected outputs on the 2026-11-01 saved resume are recorded in `comparison_results.json`. Never package or publish a real resume without consent.
