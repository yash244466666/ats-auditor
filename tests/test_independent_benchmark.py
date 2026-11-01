import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1]/'benchmarks'))
from compare_independent import evaluate, RESUMES, JOBS_BY_ID
from ats_auditor.engine import score_resume


def test_new_cross_resume_calibration_improves_aggregate_error():
    z=evaluate()
    assert z['mean_abs_error_after'] < z['mean_abs_error_before']
    assert z['mean_abs_error_after'] < 7


def test_matching_specialist_outscores_mismatched_role():
    ruby=RESUMES['rails']; js_role=JOBS_BY_ID['smartfrontend']; ruby_role=JOBS_BY_ID['stora']
    assert score_resume(ruby,ruby_role)['overall_score'] >= score_resume(ruby,js_role)['overall_score']+35


def test_fully_relevant_frontend_outscores_unrelated_frontend_resume():
    role=JOBS_BY_ID['smartfrontend']
    assert score_resume(RESUMES['frontend'],role)['overall_score'] > score_resume(RESUMES['rails'],role)['overall_score']


def test_context_calibration_is_explicit_and_bounded():
    r=score_resume(RESUMES['backend'],JOBS_BY_ID['plentific'])
    assert 0 <= r['overall_score'] <= 100
    context=r['details']['calibration_context']
    assert context['professional_experience_coverage_ratio'] > 0.5
    assert context['experience_boost_points'] > 0


def test_context_bonus_does_not_depend_on_repetition_of_skills_header():
    resume=RESUMES['frontend']; role=JOBS_BY_ID['smartfrontend']
    regular=score_resume(resume,role)['details']['calibration_context']['professional_experience_coverage_ratio']
    repeated=score_resume(resume + '\nSKILLS\n'+ 'React Next.js TypeScript ' * 20, role)['details']['calibration_context']['professional_experience_coverage_ratio']
    assert regular==repeated
