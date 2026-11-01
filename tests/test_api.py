from pathlib import Path
from fastapi.testclient import TestClient
from ats_auditor.api import app

BASE = Path(__file__).parents[1]
JOB = (BASE / 'examples' / 'truey_job.txt').read_text()
RESUME = (BASE / 'examples' / 'synthetic_resume.txt').read_text()
client = TestClient(app)


def test_health():
    assert client.get('/health').json()['status'] == 'ok'


def test_score_route_and_response_contract():
    response = client.post('/v1/get_resume_ats_score', json={'resume_text':RESUME, 'job_description':JOB,
                                                          'session_id':'api-test'})
    assert response.status_code == 200, response.text
    result = response.json()
    for key in ['id','job_description_id','overall_score','keywords','content','details']:
        assert key in result
    assert isinstance(result['keywords'],list)
    assert all({'keyword','importance','score','present'} <= set(k) for k in result['keywords'])
    update = client.post('/v1/score', json={'job_description_id':result['job_description_id'],
                                           'resume_text':RESUME+'\nReviewed pull requests.',
                                           'session_id':'api-test'})
    assert update.status_code == 200, update.text


def test_api_rejects_bad_requests():
    assert client.post('/v1/score', json={}).status_code == 422
    assert client.post('/v1/score', json={'resume_text':'a', 'job_description':JOB}).status_code == 422


def test_web_app_is_available():
    response=client.get('/')
    assert response.status_code == 200
    assert 'ATS Auditor' in response.text
    assert 'Analyze resume' in response.text


def test_http_supports_requirement_fit_mode():
    r=client.post('/v1/score',json={'resume_text':RESUME,'job_description':JOB,
                                     'session_id':'api-requirement-fit','mode':'requirement_fit'})
    assert r.status_code==200,r.text
    assert r.json()['details']['mode']=='requirement_fit'


def test_production_auth_requires_configured_token(monkeypatch):
    monkeypatch.setenv('ATS_DEPLOYMENT_MODE','production')
    monkeypatch.delenv('ATS_API_KEY',raising=False)
    r=client.post('/v1/score',json={'resume_text':RESUME,'job_description':JOB})
    assert r.status_code==503
    monkeypatch.setenv('ATS_API_KEY','test-secret-not-for-deployment')
    r=client.post('/v1/score',json={'resume_text':RESUME,'job_description':JOB})
    assert r.status_code==401
    r=client.post('/v1/score',headers={'x-api-key':'test-secret-not-for-deployment'},
                  json={'resume_text':RESUME,'job_description':JOB})
    assert r.status_code==200


def test_invalid_resume_does_not_corrupt_cached_session():
    from ats_auditor.service import ATSService
    svc=ATSService()
    first=svc.analyze(resume_text=RESUME,job_description=JOB,session_id='cache-safe')
    try:
        svc.analyze(resume_text='a',job_description_id=first['job_description_id'],session_id='cache-safe')
    except ValueError:pass
    else:assert False,'expected error'
    again=svc.analyze(job_description_id=first['job_description_id'],session_id='cache-safe')
    assert again['overall_score']==first['overall_score']
