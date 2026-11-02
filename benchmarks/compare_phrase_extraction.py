"""Evaluate the new training-phrase extractor, preserving the recorded baseline."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import subprocess

from evaluate_skillspan import (
    ROOT, SHA256, SNAPSHOT, digest, evaluate, load_split, novel_sentences, revision, write_json,
)
from ats_auditor.phrases import extract_requirements, lexicon
from ats_auditor.requirement_fit import STOP_TERMS, VOCAB


def predict(tokens, unused_terms=()):
    text = ' '.join(tokens)
    starts, ends, cursor = {}, {}, 0
    for i, token in enumerate(tokens):
        starts[cursor] = i
        ends[cursor + len(token)] = i + 1
        cursor += len(token) + 1
    vocabulary = [t for t in VOCAB if t.name.casefold() not in STOP_TERMS]
    requirements = extract_requirements(text, vocabulary, max_terms=10_000)
    spans, unaligned = set(), set()
    for requirement in requirements:
        for a, b in requirement['spans']:
            if a in starts and b in ends:
                spans.add((starts[a], ends[b]))
            else:
                unaligned.add((a, b))
    return spans, len(unaligned)


def hashes():
    paths = [*sorted((ROOT / 'src/ats_auditor').glob('*.py')),
             ROOT / 'src/ats_auditor/data/skillspan_phrases.json',
             Path(__file__), ROOT / 'benchmarks/evaluate_skillspan.py',
             ROOT / 'benchmarks/build_skillspan_lexicon.py']
    return {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in paths}


def run(cache: Path, output: Path, split: str):
    output.mkdir(parents=True, exist_ok=False)
    source_hashes = hashes()
    baseline_path = ROOT / 'benchmarks/public_skillspan/runs/verified-baseline-2026-11-02/results.json'
    baseline_hash = digest(baseline_path.read_bytes())
    protocol = {
        'schema_version': 1, 'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'git_commit': revision(), 'python': sys.version.split()[0], 'source_sha256': source_hashes,
        'tracked_working_tree_dirty': bool(subprocess.check_output(
            ['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip()),
        'dataset_commit': SNAPSHOT, 'dataset_sha256': SHA256, 'split': split,
        'lexicon_training': lexicon(), 'baseline_result_sha256': baseline_hash,
        'coefficient_fitting': False, 'test_used_to_build_lexicon': False,
        'test_status': 'Observed benchmark; not a new untouched holdout',
        'method': 'Uncapped runtime phrase extractor with explicit-negative job filtering; exact untyped spans',
        'resume_fit_or_hiring_accuracy': False,
    }
    # Store training provenance and rules, but not a duplicate of all phrase entries.
    protocol['lexicon_training'] = {k: v for k, v in protocol['lexicon_training'].items() if k != 'phrases'}
    write_json(output / 'protocol.json', protocol)
    rows = load_split(cache, split)
    previous = load_split(cache, 'train') + (load_split(cache, 'dev') if split == 'test' else [])
    diagnostic = novel_sentences(rows, previous)
    baseline = json.loads(baseline_path.read_text())['evaluations']['requirement_fit_catalog'][split]
    results = {
        'split': split, 'recorded_catalog_baseline': baseline,
        'new_phrase_extractor': evaluate(rows, (), predictor=predict),
        'unique_absent_earlier_splits': evaluate(diagnostic, (), predictor=predict),
        'by_source': {s: evaluate([r for r in rows if r['source'] == s], (), predictor=predict)
                      for s in sorted({r['source'] for r in rows})},
    }
    if hashes() != source_hashes or digest(baseline_path.read_bytes()) != baseline_hash:
        raise ValueError('Source or baseline changed during evaluation')
    for s in ('train', 'dev', 'test') if split == 'test' else ('train', 'dev'):
        if digest((cache / f'{s}.jsonl').read_bytes()) != SHA256[s]:
            raise ValueError('Dataset changed during evaluation')
    write_json(output / 'results.json', results)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=ROOT / 'benchmarks/.cache/skillspan')
    parser.add_argument('--split', choices=('dev', 'test'), default='dev')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.cache, args.output, args.split)
    print(json.dumps({k: result[k]['union_exact_span'] for k in
                      ('recorded_catalog_baseline', 'new_phrase_extractor', 'unique_absent_earlier_splits')}, indent=2))


if __name__ == '__main__':
    main()
