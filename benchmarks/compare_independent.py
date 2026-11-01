"""Compare stored black-box responses against independent fictional resume pairs.

The historical comparison is NOT a fresh blind test. For research reproducibility
these pairs use fictional and non-personal resumes. Missing source replies are
never synthesized. This script does not connect to Upplai or consume credits.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.extend([str(Path(__file__).parents[1] / 'src'), str(Path(__file__).parent)])
from independent_resumes import RESUMES
from bench_data import JOBS
from ats_auditor.source_approx import score_source_approx

DATA = json.loads((Path(__file__).parent / 'independent_results.json').read_text())
JOBS_BY_ID = {row['id']: row['description'] for row in JOBS}

def evaluate() -> dict:
    cases=[]
    for case in DATA['cases']:
        resume, jd = RESUMES[case['resume']], JOBS_BY_ID[case['job']]
        before = score_source_approx(resume, jd, parameters={'experience_slope': 0, 'coverage_floor': 0})['overall_score']
        after = score_source_approx(resume, jd)['overall_score']
        cases.append({**case,'old_score':before,'new_score':after,
                      'error_old':abs(before-case['source_score']),
                      'error_new':abs(after-case['source_score'])})
    return {
        'mean_abs_error_before':round(sum(c['error_old'] for c in cases)/len(cases),2),
        'mean_abs_error_after':round(sum(c['error_new'] for c in cases)/len(cases),2),
        'source':'Upplai tool responses recorded in a prior conversation turn',
        'limitations':'Small development/calibration set. Holdout cases were also inspected during formula exploration; results are NOT truly blind accuracy estimates.',
        'cases':cases,
    }

if __name__=='__main__':
    print(json.dumps(evaluate(),indent=2))
