from ats_auditor.engine import score_resume
from ats_auditor.source_approx import score_source_approx, _extract

RESUME = ("Example Software Engineer\nexample@example.com\nSkills: Python FastAPI PostgreSQL React TypeScript\n"
          "Experience\n" + ("Developed Python FastAPI services and React TypeScript interfaces, wrote tests.\n" * 10))
JOB = ("Backend/Frontend Engineer: Python FastAPI React TypeScript PostgreSQL AWS Kubernetes Celery. "
       "Use AWS and Kubernetes to deliver reliable production Python APIs. "
       "Implement PostgreSQL schema changes and Redis caching. "
       "Build React and TypeScript interfaces and automated tests.")

def test_calibrated_score_outputs_all_recognized_job_skills_including_missing():
    result = score_resume(RESUME, JOB, mode='compatibility')
    assert result['keyword_coverage']['total'] >= 10
    rows = {x['keyword']: x for x in result['keywords']}
    assert rows['AWS']['present'] is False
    assert rows['Kubernetes']['present'] is False
    assert rows['React']['present'] is True
    assert 0 <= result['overall_score'] <= 100


def test_calibrated_score_increases_with_valid_evidence():
    baseline = score_resume(RESUME, JOB, mode='compatibility')['overall_score']
    more = RESUME + "\nBuilt secure Kubernetes workloads on AWS; implemented Redis caching and Celery jobs.\n" * 2
    result = score_resume(more, JOB, mode='compatibility')['overall_score']
    assert result >= baseline


def test_calibrated_legacy_modes_are_separate():
    a = score_resume(RESUME, JOB, mode='legacy_frequency')
    b = score_resume(RESUME, JOB, mode='compatibility')
    c = score_resume(RESUME, JOB, mode='evidence')
    assert all('overall_score' in r for r in (a,b,c))
    assert b['details']['mode'] == 'compatibility'
    assert b['details']['scoring_method'].startswith('experimental')
    assert c['details']['mode'] == 'evidence'


def test_scoring_is_repeatable():
    a=score_source_approx(RESUME, JOB)
    b=score_source_approx(RESUME, JOB)
    assert a==b
