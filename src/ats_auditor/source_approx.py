"""Experimental general-purpose Upplai-like lexical scorer, trained only on public job briefs.

NOT Upplai source code. Not an official hiring ATS score. The extractor uses a
static cross-sector vocabulary, and matches terms actually present in each JD.
No job/company identifiers, source scores, or user data are hard-coded here.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from .engine import CATALOG, Keyword, _occurrences, _round

# A broader job-vocabulary than the original developer-focused skill list.
# Includes missing requirements; avoids restricting extraction to a fixed
# number of *matched* keywords. Phrase extraction intentionally favors
# technically verifiable requirements over general marketing words.
MORE_TERMS = '''
AWS|Amazon Web Services
Kubernetes|K8s
Celery
Sidekiq
ActiveRecord
Hotwire
Turbo
ViewComponents
Sass
BEM
Minitest
Capybara
Selenium
Stripe Connect
Billing
Heroku
Material UI|MUI
Emotion
Redux Toolkit
Formik
Yup
Apollo Client
Axios
Pydantic
Typesense
OAuth
HIPAA
FHIR
CQRS
Vite
LaunchDarkly
MSW
testcontainers
Salesforce
Slack
Google APIs
file uploads
PDF generation
digital signatures
unit tests|unit testing
REST|RESTful
access control
logging
observability
microservices
service-oriented APIs
technical designs
ERDs|entity relationship diagrams
relational data
SQL
production deployment|deployment
cloud infrastructure
software architecture
distributed systems
event-driven architecture
background jobs
API routes
App Router
server components
middleware
RBAC|role-based access control
admin portals|administration portals
dashboards
WCAG
frontend test automation
modern JavaScript
backend API integration
API gateway
DynamoDB
AWS Lambda
serverless architecture
LLM|large language model
streaming
Pydantic
DevSecOps
networking fundamentals
Golang|Go
Russian
English
ClickHouse
software modernization
software supply chain
vulnerabilities|vulnerability
vulnerability research
vulnerability management
vulnerability disclosure
CVE intake
threat model|threat modeling|threat models
cloud security
application security
security reviews
security incidents|security incident triage
security testing
secure practices
secure pipelines
SSRF
injection|SQL injection|command injection
unsafe deserialization
secrets exposure
tenant isolation
Semgrep
Bandit
CodeQL
Burp Suite
SAST
DAST
SBOM
Sigstore
Cosign
Snyk
Grype
Trivy
container security
authentication flows
API security
web security
Docker
GitLab CI
Jenkins
GraphQL Apollo Client
Strawberry GraphQL
database migrations
relational databases
production-grade applications
user interface
technical leadership
project management
coding tools
AI agents
AI-assisted coding
codebase
code reviews
performance optimization
monitoring
QA
integrations
full-stack engineering
API|APIs
React Testing Library
TypeScript
Postgres
frontend
backend
software
production
security
performance
privacy
CI/CD
'''

EXTENDED = tuple(Keyword(row.split('|')[0].strip(), tuple(p.strip() for p in row.split('|')[1:]))
                 for row in MORE_TERMS.strip().splitlines() if row.strip())

def _catalog():
    result=[]; seen=set()
    for term in (*CATALOG, *EXTENDED):
        k=term.name.casefold()
        if k not in seen:
            result.append(term);seen.add(k)
    return tuple(result)
ALL_TERMS = _catalog()


def _role_term_weight(term: Keyword, jd: str, count: int) -> float:
    # Job-frequency-based salience. Can be inspected/adjusted without
    # retraining a black-box model.
    return 1.0 + (1.4 if count >= 4 else 0.8 if count >= 3 else 0.35 if count >= 2 else 0)


def _extract(jd: str, max_terms: int = 75):
    items=[]
    for term in ALL_TERMS:
        n=len(_occurrences(term,jd))
        if n:
            items.append((term,n))
    # Always retain high frequency terms, then preserve distinct technologies
    # with one mention. The default max is high enough for diverse postings.
    if len(items)>max_terms:
        items=sorted(items,key=lambda x:(-x[1],-len(x[0].name)))[:max_terms]
    return items


# Rounded coefficients fitted to eight observed black-box comparisons. The
# five-family initial development set and role-focused checks are documented
# in benchmarks/. Coefficients are not evidence of Upplai's internal formula.
CALIBRATED_DEFAULTS = {
    "a": 1.4, "exp": 2.25, "mul": 2.0,
    "jw": 1.0, "tw": 10.0, "gw": 0.2,
    "offset": -4.0, "max_terms": 75,
    "experience_threshold": 0.36, "experience_slope": 150.0,
    "experience_min_coverage": 0.40, "coverage_floor": 26.0,
}
GENERAL_WORDS = {"software", "production", "performance", "frontend", "backend",
                 "api", "integrations", "security", "databases", "ai", "full-stack",
                 "bug fixing", "git", "code review", "unit testing", "integration testing"}


def score_source_approx(resume: str, jd: str, *, parameters: dict | None = None, max_keywords: int | None = None):
    """Reproducible Upplai-style overall/keyword compatibility estimate.

    Estimates are fitted to observed *overall* responses, but this is not
    Upplai code or an official Applicant Tracking System evaluation.
    """
    if len(resume.strip()) < 100 or len(jd.strip()) < 50:
        raise ValueError("Full resume and job description required")
    p = dict(CALIBRATED_DEFAULTS)
    p.update(parameters or {})
    if max_keywords is not None:
        p["max_terms"] = max_keywords
    terms = _extract(jd, max_terms=int(p["max_terms"]))
    if not terms:
        raise ValueError("No matching skill/requirement phrases found")
    head = jd[:125]
    total = weight_sum = 0.0
    rows = []
    for term, job_mentions in terms:
        occurrences = len(_occurrences(term, resume))
        title_mention = bool(_occurrences(term, head))
        is_general = term.name.casefold() in GENERAL_WORDS
        weight = ((1 + p["jw"] * max(0, job_mentions - 1))
                  * (1 + p["tw"] * title_mention)
                  * (p["gw"] if is_general else 1))
        match_ratio = (occurrences / (occurrences + p["a"] * job_mentions)) if occurrences else 0.0
        per_term_score = 100 * min(1, p["mul"] * match_ratio ** p["exp"])
        total += per_term_score * weight
        weight_sum += weight
        rows.append({"keyword":term.name,"present":bool(occurrences),
                     "score":_round(per_term_score),
                     "importance":("very high" if job_mentions>=4 else "high" if job_mentions>=3
                                   else "medium" if job_mentions>=2 else "low"),
                     "resume_mentions":occurrences,"job_mentions":job_mentions})
    # Second-stage context calibration (v0.4): the original lexical model
    # strongly under-scored *specialist* resumes with deeply relevant work
    # examples. Apply an interpretable, capped uplift based on DISTINCT job
    # requirements actually mentioned in professional experience, rather
    # than frequency of keyword repetitions. This is empirical calibration,
    # NOT a claim about Upplai's private implementation.
    baseline_score = _round(total / max(.001, weight_sum) + p["offset"])
    matched_count = sum(bool(r["resume_mentions"]) for r in rows)
    coverage = matched_count / len(rows)
    match = re.search(r"(?im)^\s*(?:EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT|PROFESSIONAL EXPERIENCE)\s*$", resume)
    professional_text = ""
    if match:
        remainder = resume[match.end():]
        next_section = re.search(r"(?im)^\s*(?:EDUCATION|CERTIFICATIONS|PROJECTS|AWARDS)\s*$", remainder)
        professional_text = remainder[:next_section.start()] if next_section else remainder
    professional_coverage = (
        sum(bool(_occurrences(term, professional_text)) for term, _ in terms) / len(rows)
        if professional_text else 0.0
    )
    min_floor = _round(p["coverage_floor"] * coverage) if matched_count else 0
    professional_boost = 0
    if coverage >= p["experience_min_coverage"] and professional_text:
        professional_boost = _round(p["experience_slope"] * max(
            0.0, professional_coverage - p["experience_threshold"]))
    # Partial-role credit for genuine cross-stack positions: a specialist may
    # cover an entire frontend or backend half without matching both halves.
    # This is a score floor, not a keyword-frequency multiplier. It activates
    # only when the JD explicitly calls for full-stack engineering and names
    # requirements in BOTH families. Company/job names play no role.
    def _family_fraction(labels: tuple[str, ...]) -> tuple[float, int]:
        family = [(t, n) for t, n in terms if t.name.casefold() in labels]
        if not family:
            return (0.0, 0)
        observed = sum(bool(_occurrences(t, professional_text)) for t, _ in family)
        return observed / len(family), len(family)

    frontend_names = frozenset({"react", "typescript", "next.js", "vue.js",
        "redux toolkit", "material ui", "tailwind css", "zustand", "css", "html", "vite"})
    backend_names = frozenset({"python", "fastapi", "django", "postgresql", "redis",
        "dynamodb", "aws lambda", "api gateway", "serverless architecture", "pydantic",
        "node.js", "ruby on rails", "sqlalchemy", "aws", "kubernetes", "celery"})
    front_rate, front_count = _family_fraction(frontend_names)
    back_rate, back_count = _family_fraction(backend_names)
    partial_role_floor = 0
    explicitly_fullstack = bool(re.search(r"(?i)full[- ]stack", jd[:160]))
    if (explicitly_fullstack and professional_text and front_count >= 2 and back_count >= 3
            and coverage < 0.55 and max(front_rate, back_rate) >= 0.35):
        partial_role_floor = _round(15 + 20 * max(front_rate, back_rate))
    overall = _round(max(max(baseline_score, min_floor) + professional_boost,
                         partial_role_floor))
    return {"overall_score":overall,
            "keyword_coverage":{"matched":sum(k["present"] for k in rows),"total":len(rows)},
            "keywords":[{key:r[key] for key in ("keyword","present","importance","score")} for r in rows],
            "details":{"mode":"compatibility","scoring_method":"experimental Upplai-like calibration over public-job benchmarks",
                       "calibration_context": {"raw_lexical_score": baseline_score,
                            "keyword_coverage_ratio": round(coverage, 4),
                            "professional_experience_coverage_ratio": round(professional_coverage, 4),
                            "experience_boost_points": professional_boost,
                            "coverage_floor_points": min_floor,
                            "partial_cross_stack_role_floor": partial_role_floor,
                            "frontend_experience_fraction": round(front_rate,4),
                            "backend_experience_fraction": round(back_rate,4),
                            "generalization_warning": (
                                "HIGH UNCERTAINTY: fewer than 40% of extracted job requirements were recognized in the resume; "
                                "cross-domain skills can be scored differently by Upplai."
                                if coverage < 0.40 else
                                "LIMITED VALIDATION: calibrated on a small software-engineering sample, not a blind ATS replica.")},
                       "parameters":p,
                       "keyword_counts":[{"keyword":r["keyword"],"job_mentions":r["job_mentions"],
                                          "resume_mentions":r["resume_mentions"]} for r in rows],
                       "limitations":["Not Upplai source code; estimates calibrated on a small software-jobs sample, and uncertain on unseen job families.",
                                      "This score is NOT a prediction of hiring or official ATS behavior."]}}
