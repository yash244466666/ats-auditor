from pathlib import Path
from ats_auditor.engine import Keyword, _occurrences, extract_keywords, score_resume
from ats_auditor.service import ATSService

BASE = Path(__file__).parents[1]
JOB = (BASE / 'examples' / 'truey_job.txt').read_text()
RESUME = (BASE / 'examples' / 'synthetic_resume.txt').read_text()


def test_keyword_catalog_detects_truey_terms():
    names = [x['term'].name for x in extract_keywords(JOB, max_keywords=60)]
    for term in ('AI','React','TypeScript','Python','FastAPI','PostgreSQL','Redis',
                 'pytest','Testing Library','authentication','caching','LangGraph'):
        assert term in names, term


def test_phrase_boundaries_aliases():
    assert len(_occurrences(Keyword('AI'), 'OpenAI is not AI, but AI is AI.')) == 3
    assert len(_occurrences(Keyword('PostgreSQL', ('Postgres',)), 'PostgreSQL and Postgres')) == 2
    assert len(_occurrences(Keyword('full-stack', ('full stack',)), 'full-stack full stack')) == 2
    assert len(_occurrences(Keyword('Python'), 'Pythonic Python')) == 1


def test_score_bounded_and_missing_terms_zero():
    out = score_resume(RESUME, JOB)
    assert 0 <= out['overall_score'] <= 100
    assert out['keyword_coverage']['total'] > 5
    assert all(0 <= item['score'] <= 100 for item in out['keywords'])
    assert all(item['score'] == 0 for item in out['keywords'] if not item['present'])


def test_frequency_sensitive_compat_mode():
    repeated = RESUME + '\n' + ('\nFastAPI Python React Redis pytest Docker TypeScript PostgreSQL' * 8)
    before = score_resume(RESUME, JOB, mode='legacy_frequency')
    after = score_resume(repeated, JOB, mode='legacy_frequency')
    assert after['overall_score'] >= before['overall_score']
    assert after['details']['keyword_stuffing_warnings']


def test_evidence_mode_discourages_stuffing():
    repeated = RESUME + '\n' + ('\nLangGraph LangChain OpenAI caching authentication' * 15)
    before = score_resume(RESUME, JOB, mode='evidence')
    after = score_resume(repeated, JOB, mode='evidence')
    assert after['overall_score'] <= before['overall_score']


def test_contextual_evidence_matters_more_than_list():
    job = 'Build Python FastAPI production APIs with PostgreSQL, Redis, testing, authentication and React.'
    skill_only = ('Sample Developer\nexample@example.com\nSkills: Python, FastAPI, PostgreSQL, Redis, React, authentication.\n'
                  'Experience\n' + 'General engineering work supporting a software team.\n' * 20)
    proof = skill_only + ('Built Python FastAPI APIs in PostgreSQL and reduced response latency 25%.\n'
                          'Implemented Redis caching and JWT authentication for React requests.\n')
    a = score_resume(skill_only, job, mode='evidence')
    b = score_resume(proof, job, mode='evidence')
    assert b['overall_score'] > a['overall_score']


def test_session_reuse_and_isolation():
    s = ATSService()
    initial = s.analyze(resume_text=RESUME, job_description=JOB, session_id='alice')
    jid = initial['job_description_id']
    updated = s.analyze(resume_text=RESUME+'\nMore CI/CD testing.', job_description_id=jid, session_id='alice')
    assert initial['job_description_id'] == updated['job_description_id']
    next_job = s.analyze(job_description=JOB.replace('TypeScript', 'JavaScript'), session_id='alice')
    assert next_job['job_description_id'] != jid
    try:
        s.analyze(resume_text=RESUME, job_description_id=jid, session_id='bob')
    except ValueError as e:
        assert 'Unknown' in str(e)
    else:
        assert False, 'Job IDs should not cross sessions'


def test_invalid_input_rejected():
    s = ATSService()
    for kwargs in ({'resume_text': RESUME}, {'job_description': JOB},
                   {'resume_text':'short','job_description':JOB}):
        try:
            s.analyze(**kwargs)
        except ValueError:
            continue
        assert False, f'Expected rejection of {list(kwargs)}'


def test_synthetic_stress_test_can_game_frequency_score():
    terms = [k['term'].name for k in extract_keywords(JOB, max_keywords=20)]
    stress = RESUME + '\nBENCHMARK ONLY\n' + (' '.join(terms) + '\n') * 45
    low = score_resume(RESUME, JOB, mode='legacy_frequency')
    high = score_resume(stress, JOB, mode='legacy_frequency')
    assert high['overall_score'] == 100
    assert high['overall_score'] > low['overall_score']
    assert high['details']['keyword_stuffing_warnings']
    quality = score_resume(stress, JOB, mode='evidence')
    assert quality['overall_score'] < high['overall_score']
