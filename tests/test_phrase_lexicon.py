"""Train-only builder and phrase offsets, using fictional annotations."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'benchmarks'))
from build_skillspan_lexicon import build
from ats_auditor.phrases import PhraseMatcher, extract_requirements, lexicon
from ats_auditor.engine import Keyword


def record(idx, tokens, tags):
    return {'idx': idx, 'source': 'fictional', 'tokens': tokens,
            'tags_skill': tags, 'tags_knowledge': ['O'] * len(tokens)}


def test_builder_requires_distinct_training_documents_and_positive_contexts():
    same = record(1, ['widget', 'design'], ['B', 'I'])
    assert build([same, same])['phrases'] == []
    other = record(2, ['widget', 'design'], ['B', 'I'])
    assert build([same, other])['phrases'] == ['widget design']
    negatives = [record(i, ['widget', 'design'], ['O', 'O']) for i in range(3, 8)]
    assert build([same, other, *negatives])['phrases'] == []


def test_phrase_matcher_normalizes_case_punctuation_and_keeps_character_offsets():
    matcher = PhraseMatcher(['widget design', 'design', 'c++'])
    text = 'WIDGET  design, C + +.'
    hits = matcher.find(text)
    assert [(h.name, text[h.start:h.end]) for h in hits] == [('widget design', 'WIDGET  design'), ('c++', 'C + +')]
    assert len(matcher.find(text, longest_only=False)) == 3


def test_alias_and_lexicon_occurrences_are_not_lost_or_double_counted():
    job = 'Stakeholder management and stakeholder management. Postgres and PostgreSQL.'
    rows = extract_requirements(job, [Keyword('PostgreSQL', ('Postgres',))])
    by_name = {r['term'].name: r for r in rows}
    assert by_name['stakeholder management']['job_mentions'] == 2
    assert by_name['PostgreSQL']['job_mentions'] == 2
    assert by_name['stakeholder management']['origin'] == 'skillspan_train'


def test_bundled_data_declares_training_split_and_separate_license():
    data = lexicon()
    assert data['split_used'] == 'train'
    assert data['license'] == 'CC-BY-4.0'
    assert data['rules']['min_distinct_training_documents'] >= 2


def test_explicitly_optional_or_denied_job_terms_are_not_requirements():
    terms = [Keyword('Python'), Keyword('Linux'), Keyword('authentication', ('authorization',))]
    rows = extract_requirements('Linux is required. Python experience is not required. Work authorization is checked separately.', terms)
    assert {r['term'].name for r in rows} == {'Linux'}
