"""Calibrate ONLY on training job postings; holdout scores are reported untouched.
Use random-search over a small, interpretable parameter space rather than
hardcoding reference scores or companies into the scoring engine.
"""
import json
import random
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from bench_data import JOBS
from ats_auditor.source_approx import _extract, _occurrences
ROOT=Path(__file__).parents[1]
resume=(Path('/mnt/data')/'Truey — Mid-level Full-Stack Engineer — Targeted Resume (Draft).txt').read_text()
base=[]
for j in JOBS:
    terms=[(t.name,n,len(_occurrences(t,resume))) for t,n in _extract(j['description'],max_terms=120)]
    base.append({**j,'terms':terms})

def calculate(job,p):
    items=job['terms']
    max_terms=int(p['max_terms'])
    if len(items)>max_terms:
        items=sorted(items,key=lambda t:(-t[1],-len(t[0])))[:max_terms]
    sum_score=sum_weight=0
    for name,jn,occ in items:
        imp=1+(1.4 if jn>=4 else .8 if jn>=3 else .35 if jn>=2 else 0)*p['frequency_weight']
        item=min(1.,p['base_hit']+(occ-1)*p['extra_hit'])/(1+p['jd_demand']*max(0,jn-1)) if occ else 0
        sum_score+=item*imp
        sum_weight+=imp
    return round(max(0.,min(100.,100*sum_score/max(0.01,sum_weight)+p['offset'])))

def score(p,split='train'):
    errs=[calculate(j,p)-j['upplai'] for j in base if j['split']==split]
    return sum(abs(d) for d in errs)/len(errs), sum(d*d for d in errs)/len(errs)

rng=random.Random(28029)
params=[]
for i in range(24000):
    p={'base_hit':rng.uniform(.03,.55),'extra_hit':rng.uniform(.01,.23),'frequency_weight':rng.uniform(0,2.4),
       'jd_demand':rng.uniform(0,1.5),'offset':rng.uniform(-12,6),'max_terms':rng.choice([35,40,45,50,55,60,65,70,75,85,95])}
    mae,mse=score(p)
    # retain an engineering-practical bounded intercept
    ranking=mae+0.05*mse+0.18*abs(p['offset'])
    params.append((ranking,p,mae,mse))
params.sort(key=lambda x:x[0]);p=params[0][1]
print('Best train:',round(params[0][2],2),'RMSE',round(params[0][3]**.5,2),'params',p)
print('Holdout:',tuple(round(z,2) for z in score(p,'holdout')))
for j in base:
 print(f"{j['id']:14s} {j['split']:8s} source {j['upplai']:2d}, predicted {calculate(j,p):2d}, delta {calculate(j,p)-j['upplai']:+3d}, distinct {len(j['terms'])}")
ROOT.joinpath('benchmarks','calibration.json').write_text(json.dumps({'parameters':p,'train_MAE':score(p)[0], 'holdout_MAE':score(p,'holdout')[0],
 'cases':[{'id':j['id'],'split':j['split'],'upplai':j['upplai'],'prediction':calculate(j,p),'source':j['source']} for j in base]},indent=2)+'\n')
