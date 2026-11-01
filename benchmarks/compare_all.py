"""One-command benchmark comparison of recorded Upplai scores and local scorer.

Usage: python benchmarks/compare_all.py --resume /path/to/private-resume.txt
Reference answers were observed externally; do not call the third-party API.
"""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from bench_data import JOBS
from ats_auditor.engine import score_resume

p=argparse.ArgumentParser();p.add_argument('--resume',required=True)
a=p.parse_args();resume=Path(a.resume).read_text(encoding='utf-8')
rows=[]
for j in JOBS:
 old=score_resume(resume,j['description'],mode='legacy_frequency')['overall_score']
 new=score_resume(resume,j['description'],mode='compatibility')['overall_score']
 evidence=score_resume(resume,j['description'],mode='evidence')['overall_score']
 rows.append({'job':j['id'],'split':j['split'],'source':j['source'],'upplai':j['upplai'],
              'legacy':old,'calibrated':new,'evidence':evidence,'abs_error_before':abs(old-j['upplai']),
              'abs_error_after':abs(new-j['upplai'])})
print(json.dumps({'mean_absolute_error_legacy':round(sum(r['abs_error_before'] for r in rows)/len(rows),2),
                  'mean_absolute_error_calibrated':round(sum(r['abs_error_after'] for r in rows)/len(rows),2),
                  'note':'Development-set fit; NOT a held-out generalization estimate. Job postings summarized faithfully, not copied verbatim.',
                  'cases':rows},indent=2))
