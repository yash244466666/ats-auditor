"""Independent requirements-fit heuristic (NOT an Upplai score).

Designed for human-inspectable role matching across software, security, and data jobs.
Count each canonical requirement once: repetitions do not inflate fit.
"""
from __future__ import annotations

from collections import defaultdict
from .engine import CATALOG, Keyword, _occurrences, _round, _sectioned_lines
from .source_approx import EXTENDED

EXTRA = '''
Apache Spark|Spark|PySpark
Apache Airflow|Airflow
Snowflake
DBT|dbt
Kafka
Apache Iceberg|Iceberg
Parquet
ELT|ETL
Data engineering
Data quality
Data pipelines
Data modeling|data models
Data warehouse|data warehouses
Lakehouse|data lake
Data lineage
ETL pipelines
AWS Glue
AWS S3|S3
AWS EMR|EMR
Terraform
Azure
GCP|Google Cloud
RabbitMQ
Resque
RSpec
CSRF
Devise
OWASP
Penetration testing|pentesting
Secure code review|source code review
Cryptography
OIDC
OAuth2
JWT
SQL injection
SSRF
Application Security
Security vulnerabilities
Threat modeling
Incident response
Secrets management
SAST
DAST
WCAG
Core Web Vitals
Accessibility
Next.js App Router
React 19
Figma
SEO
Responsive design
State management
API integration
Server-side rendering
IDOR
Hotwire
Turbo
Git
Python
Ruby
Rails
Java
TypeScript
React
Redis
API contracts
Testing Library
Stripe
API design

'''
STOP_TERMS={'software','production','performance','frontend','backend','api','APIs',
            'integrations','security','ai','git','privacy','codebase','project management',
            'monitoring','debugging','code reviews','software architecture','code review',
            'full-stack engineering','full-stack','user interface','coding tools','technical designs',
            'leadership','development','English','professional experience'}

def vocab():
    result={}
    for term in (*CATALOG, *EXTENDED, *(Keyword(r.split('|')[0].strip(),tuple(s.strip() for s in r.split('|')[1:])) for r in EXTRA.strip().splitlines() if r.strip())):
        name=term.name.lower()
        if name not in result:
            result[name]=term
        else:
            base=result[name]
            result[name]=Keyword(base.name,tuple(dict.fromkeys((*base.aliases,*term.aliases))))
    return list(result.values())

VOCAB=vocab()

def role_fit_score(resume_text:str, job_description:str, top_n:int=80) -> dict:
    if len(resume_text.strip()) <100 or len(job_description.strip()) <50:
        raise ValueError('Full resume and job description required')
    lines=_sectioned_lines(resume_text)
    # Prefer longer distinctive terms when overlaps would double-count adjacent synonyms.
    recognized=[]
    for term in VOCAB:
        count=len(_occurrences(term,job_description))
        if count==0 or term.name.casefold() in STOP_TERMS:continue
        recognized.append((term,count))
    recognized.sort(key=lambda z:(-z[1],-len(z[0].name)))
    recognized=recognized[:top_n]
    if not recognized:
        raise ValueError('No supported requirements found; need broader domain vocabulary')
    rows=[]; total=0.; found=0.
    for term,j_n in recognized:
        r_n=len(_occurrences(term,resume_text))
        title_hits=len(_occurrences(term,job_description[:140]))
        weight=1.0 + (0.75 if j_n >=3 else 0.45 if j_n==2 else 0.0) + (0.7 if title_hits else 0.0)
        # Skills list is a self-attestation, experience evidence provides context.
        contexts=[]
        for sec,line in lines:
            if _occurrences(term,line):
                if ('experience' in sec or 'project' in sec) or line[:1] in ('*','-','•'):
                    contexts.append(line[:220])
                elif any(word in line.casefold() for word in ('built ','designed ','implemented ','developed ','tested ','reviewed ','deployed ','optimized ')):
                    contexts.append(line[:220])
        # Partial credibility for self-attested skills, full credit for contextual examples.
        credit = 0.0 if not r_n else (0.85 if contexts else 0.68)
        total+=weight
        found+=weight*credit
        rows.append({'keyword':term.name,'present':bool(r_n),'job_mentions':j_n,
                    'weight':round(weight,2),'credit':round(credit,2),
                    'evidence':contexts[:2]})
    score=_round(100*found/total)
    rows.sort(key=lambda r:(-r['weight'], -r['job_mentions'],r['keyword']))
    return {'overall_score':score,'keyword_coverage':{'matched':sum(r['present'] for r in rows),'total':len(rows)},
            'keywords':[{'keyword':r['keyword'],'present':r['present'],'importance':
                         'high' if r['weight']>=2 else 'medium' if r['weight']>=1.45 else 'low',
                         'score':_round(r['credit']*100)} for r in rows],
            'details':{'mode':'requirement_fit',
                       'scoring_method':'independent requirement coverage with contextual evidence discount; not calibrated to Upplai',
                       'requirement_weights':rows,
                       'limitations':['Skills written in a resume are claims, not verification.',
                                      'Text-only assessment; eligibility and document layout assessed separately.',
                                      'Industry-specific vocabulary is incomplete.']}}
