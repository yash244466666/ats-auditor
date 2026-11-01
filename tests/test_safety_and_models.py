from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / 'benchmarks'))
from independent_resumes import RESUMES
from bench_data import JOBS
from ats_auditor.engine import score_resume

JOB = {j['id']:j['description'] for j in JOBS}

def test_partial_frontend_credit_for_true_crossstack_job():
    r=score_resume(RESUMES['frontend'],JOB['taktile'])
    assert 30 <= r['overall_score'] <= 40
    assert r['details']['calibration_context']['partial_cross_stack_role_floor'] >= 30

def test_partial_crossstack_floor_does_not_apply_to_rails_only():
    r=score_resume(RESUMES['frontend'],JOB['stora'])
    assert r['details']['calibration_context']['partial_cross_stack_role_floor']==0
    assert r['overall_score'] <= 15

def test_source_compatibility_and_requirement_fit_are_distinct():
    r=RESUMES['security'];j=JOB['plentific']
    compat=score_resume(r,j,'compatibility')
    fit=score_resume(r,j,'requirement_fit')
    assert compat['details']['mode']=='compatibility'
    assert fit['details']['mode']=='requirement_fit'
    assert 'generalization_warning' in compat['details']['calibration_context']


def test_non_matching_input_does_not_generate_high_score():
    r=RESUMES['security'];j=JOB['stora']
    assert score_resume(r,j,'compatibility')['overall_score']<=10


def test_mcp_local_mode_calls_service_instead_of_recursing():
    from ats_auditor import mcp_server
    import inspect
    source = inspect.getsource(mcp_server.create_mcp)
    assert 'SERVICE.analyze(resume_text=resume_text' in source
    assert source.count('return score_safely(resume_text, job_description, job_description_id, session_id, scoring_mode)') == 1
