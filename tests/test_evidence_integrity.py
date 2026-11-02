"""Fictional regressions for requirement extraction and evidence integrity."""
import pytest

from ats_auditor.engine import score_resume

PROFILE = (
    "Casey Example\ncasey@example.test\nSUMMARY\n"
    "Fictional technician maintaining workshop inventory and supporting a local team. "
    "This profile is an invented test record, not a real applicant.\n"
)
JOB = (
    "Python developer. Required skills include Python. Build Python services for a "
    "fictional company, review application changes, and maintain reliable team workflows."
)


def python_row(result):
    return next(r for r in result['keywords'] if r['keyword'].casefold() == 'python')


@pytest.mark.parametrize('mode', ['evidence', 'requirement_fit'])
@pytest.mark.parametrize('claim', [
    'I have no experience with Python.',
    'I have never used Python.',
    'Python: no professional experience.',
    'I lack Python experience.',
    'I have not built Python services.',
])
def test_denied_skill_gets_no_credit(mode, claim):
    result = score_resume(PROFILE + '\nEXPERIENCE\n' + claim, JOB, mode)
    item = python_row(result)
    assert item['present'] is False
    assert item['score'] == 0


@pytest.mark.parametrize('mode', ['evidence', 'requirement_fit'])
def test_negation_scope_and_pseudo_negation(mode):
    positive = score_resume(PROFILE + '\nEXPERIENCE\nBuilt not only Python services but also reports.', JOB, mode)
    scoped = score_resume(PROFILE + '\nEXPERIENCE\nI never used Java, but built Python services.', JOB, mode)
    assert python_row(positive)['present'] is True
    assert python_row(scoped)['present'] is True


@pytest.mark.parametrize('mode', ['evidence', 'requirement_fit'])
def test_copied_job_text_is_not_candidate_evidence(mode):
    before = score_resume(PROFILE, JOB, mode)
    copied = score_resume(PROFILE + '\nPROFESSIONAL EXPERIENCE\n' + JOB, JOB, mode)
    assert python_row(copied)['score'] == 0
    assert copied['overall_score'] == before['overall_score']


@pytest.mark.parametrize('mode', ['evidence', 'requirement_fit'])
def test_copy_on_one_sentence_does_not_erase_separate_genuine_evidence(mode):
    resume = PROFILE + '\nEXPERIENCE\nBuilt Python invoice exports for a fictional workshop.\n'
    before = score_resume(resume, JOB, mode)
    copied = score_resume(resume + JOB, JOB, mode)
    assert python_row(before)['score'] == python_row(copied)['score']
    assert python_row(copied)['score'] > 0


@pytest.mark.parametrize('mode', ['evidence', 'requirement_fit'])
def test_learning_only_gets_less_credit_than_delivered_work(mode):
    learning = score_resume(PROFILE + '\nPROJECTS\nCurrently learning Python through tutorials.', JOB, mode)
    shipped = score_resume(PROFILE + '\nPROJECTS\nBuilt Python invoice exports for a fictional workshop.', JOB, mode)
    assert python_row(learning)['score'] < python_row(shipped)['score']


@pytest.mark.parametrize('mode', ['evidence', 'requirement_fit'])
def test_equivalent_headings_and_whitespace(mode):
    a = PROFILE + '\nTECHNICAL SKILLS\nPython\nEXPERIENCE\nBuilt Python services for a fictional workshop.'
    b = a.replace('TECHNICAL SKILLS', 'TECHNICAL  SKILLS').replace('EXPERIENCE', 'PROFESSIONAL EXPERIENCE')
    assert score_resume(a, JOB, mode)['overall_score'] == score_resume(b, JOB, mode)['overall_score']


@pytest.mark.parametrize('mode', ['evidence', 'requirement_fit'])
def test_training_phrase_extraction_and_eligibility_separation(mode):
    job = ('Reliability specialist. Linux and stakeholder management are required. '
           'Work authorization is checked separately; we do not require authentication engineering.')
    result = score_resume(PROFILE + '\nEXPERIENCE\nMaintained Linux hosts and led stakeholder management.', job, mode)
    names = {r['keyword'].casefold() for r in result['keywords']}
    assert 'linux' in names
    assert 'stakeholder management' in names
    assert 'authentication' not in names


def test_new_integrity_rules_preserve_calibrated_modes():
    # Existing calibration tests protect numeric behavior on the historical set.
    assert score_resume(PROFILE + '\nSKILLS\nPython', JOB, 'legacy_frequency')['details']['mode'] == 'legacy_frequency'


@pytest.mark.parametrize('mode', ['evidence', 'requirement_fit'])
def test_contrasting_learning_scope_is_per_skill(mode):
    result = score_resume(PROFILE + '\nEXPERIENCE\nBuilt Python exports while learning Java.', JOB, mode)
    assert python_row(result)['score'] >= 40


@pytest.mark.parametrize('mode', ['evidence', 'requirement_fit'])
def test_different_skill_action_does_not_upgrade_a_self_attestation(mode):
    plain = score_resume(PROFILE + '\nEXPERIENCE\nI know Python.', JOB, mode)
    contrasted = score_resume(PROFILE + '\nEXPERIENCE\nI know Python, but built Java applications for 200 users.', JOB, mode)
    assert python_row(plain)['score'] == python_row(contrasted)['score']


@pytest.mark.parametrize('mode', ['compatibility', 'legacy_frequency', 'evidence', 'requirement_fit'])
def test_whitespace_padding_cannot_bypass_minimum_content(mode):
    with pytest.raises(ValueError, match='incomplete'):
        score_resume('a ' * 60, JOB, mode)


def test_service_rejects_padding_without_corrupting_cached_resume():
    from ats_auditor.service import ATSService
    service = ATSService()
    good = service.analyze(PROFILE, JOB)
    with pytest.raises(ValueError, match='non-whitespace'):
        service.analyze('a ' * 60, JOB)
    repeated = service.analyze(job_description_id=good['job_description_id'])
    assert repeated['overall_score'] == good['overall_score']
