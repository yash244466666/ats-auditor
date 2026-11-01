import sys,random,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from bench_data import JOBS
from ats_auditor.source_approx import _extract,_occurrences
root=Path(__file__).parents[1]
resume=Path('/mnt/data/Truey — Mid-level Full-Stack Engineer — Targeted Resume (Draft).txt').read_text()
rows=[]
for j in JOBS+[dict(id='truey',split='train',description=(Path('/mnt/data/truey-full-job-description.txt')).read_text(),upplai=68)]:
 terms=[]
 for t,jn in _extract(j['description'],120):
  name=t.name;occ=len(_occurrences(t,resume));title=int(bool(_occurrences(t,j['description'][:125])))
  generic=name.lower() in {'software','production','performance','frontend','backend','api','integrations','security','databases','ai','full-stack','bug fixing','git','code review','unit testing','integration testing'}
  terms.append((name,jn,occ,title,generic))
 rows.append((j,terms))

def calc(j,terms,p):
 max_terms=int(p['max_terms'])
 if len(terms)>max_terms:
  terms=sorted(terms,key=lambda x:(-x[1],-len(x[0])))[:max_terms]
 total=weight=0
 for name,jn,occ,title,generic in terms:
  w=(1+p['jw']*(jn-1))*(1+p['tw']*title)*(p['gw'] if generic else 1)
  val=min(1,p['mul']*(occ/(occ+p['a']*jn))**p['exp']) if occ else 0
  total+=w*val;weight+=w
 return max(0,min(100,round(100*total/max(0.001,weight)+p['offset'])))

def eval_(p,select='train'):
 allrows=[(j,t) for j,t in rows if j['split']==select]
 er=[calc(j,t,p)-j['upplai'] for j,t in allrows]
 return sum(abs(e) for e in er)/len(er),sum(e*e for e in er)/len(er)

rng=random.Random(19422); best=[]
for i in range(42000):
 p={'a':rng.uniform(.4,6.0),'exp':rng.uniform(.4,1.9),'mul':rng.uniform(.7,1.8),'jw':rng.uniform(0,2),
    'tw':rng.uniform(0,7),'gw':rng.uniform(.2,1.1),'offset':rng.uniform(-8,7),
    'max_terms':rng.choice([40,50,55,60,65,75,90,100])}
 train_mae,mse=eval_(p,'train')
 ranking=train_mae+.045*mse+.05*abs(p['offset'])
 best.append((ranking,p,train_mae,mse))
best.sort(key=lambda x:x[0]);
for rank in [0,1,2,3]:
 p=best[rank][1];print('RANK',rank, 'train',round(best[rank][2],2),'rmse',round(best[rank][3]**.5,2),'holdout',eval_(p,'holdout'),'params',p)
 print([(j['id'],j['upplai'],calc(j,t,p)) for j,t in rows])
import json
root.joinpath('benchmarks','nonlinear_calibration.json').write_text(json.dumps({'parameters':best[0][1], 'train_MAE':best[0][2], 'holdout_MAE':eval_(best[0][1],'holdout')[0]},indent=2)+'\n')
