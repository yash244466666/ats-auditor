"""Before/after behavioral checks using the frozen fictional quality-v1 corpus.

The corpus is supplied separately (PR #16); it is observed development data,
not independent gold accuracy. Neither worker makes endpoint/LLM requests.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

from compare_phrase_extraction import hashes
from evaluate_skillspan import ROOT, digest, revision, write_json
from ats_auditor.phrases import extract_requirements
from ats_auditor.requirement_fit import STOP_TERMS, VOCAB
from ats_auditor.engine import _occurrences

MODES = ('compatibility', 'legacy_frequency', 'evidence', 'requirement_fit')
VARIANTS = ('baseline', 'negated_missing', 'copied_job', 'duplicate', 'equivalent_headings')
WORKER = '''
import json,sys
sys.path.insert(0,sys.argv[1])
from ats_auditor.engine import score_resume
cases=json.load(sys.stdin)
results=[]
for c in cases:
    for mode in ('compatibility','legacy_frequency','evidence','requirement_fit'):
        try:
            r=score_resume(c['resume'],c['job'],mode)
            results.append({'id':c['id'],'variant':c['variant'],'mode':mode,'score':r['overall_score']})
        except Exception as exc:
            results.append({'id':c['id'],'variant':c['variant'],'mode':mode,'error':type(exc).__name__})
print(json.dumps(results))
'''


def source_hashes(root: Path):
    return {str(p.relative_to(root)): digest(p.read_bytes())
            for p in sorted((root / 'ats_auditor').glob('*.py'))}


def worker(source: Path, cases: list[dict]):
    process = subprocess.run([sys.executable, '-I', '-c', WORKER, str(source)],
                             input=json.dumps(cases), capture_output=True, text=True, check=True)
    return json.loads(process.stdout)


def run(corpus: Path, baseline_source: Path, output: Path):
    manifest = json.loads((corpus / 'manifest.json').read_text())
    if manifest['corpus_id'] != 'quality-v1':
        raise ValueError('Expected the frozen fictional quality-v1 corpus')
    for name, expected in manifest['files'].items():
        if digest((corpus / name).read_bytes()) != expected:
            raise ValueError(f'Corrupt corpus: {name}')
    resumes = json.loads((corpus / 'resumes.json').read_text())
    jobs = json.loads((corpus / 'jobs.json').read_text())
    if not all(r.get('fictional') is True for r in resumes + jobs):
        raise ValueError('Only declared fictional records are permitted')
    resumes, jobs = {r['id']: r['text'] for r in resumes}, {j['id']: j['text'] for j in jobs}
    anchors = json.loads((corpus / 'labels.json').read_text())
    before_hashes, current_hashes = source_hashes(baseline_source), hashes()
    runner_hash = digest(Path(__file__).read_bytes())
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / 'protocol.json', {
        'started_at_utc': datetime.now(timezone.utc).isoformat(), 'git_commit': revision(),
        'baseline_git_commit': subprocess.check_output(['git', '-C', str(baseline_source), 'rev-parse', 'HEAD'], text=True).strip(),
        'tracked_working_tree_dirty': bool(subprocess.check_output(
            ['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip()),
        'current_source_sha256': current_hashes, 'baseline_source_sha256': before_hashes,
        'worker_sha256': digest(WORKER.encode()), 'runner_sha256': runner_hash,
        'corpus_sha256': manifest['files'], 'anchors': len(anchors), 'modes': MODES,
        'variants': VARIANTS, 'planned_calls_per_worker': len(anchors) * len(MODES) * len(VARIANTS),
        'status': 'Known fictional development cases, not independent semantic gold or hiring accuracy',
        'recipes': {
            'negated_missing': 'Append one I have no experience with TERM. line per absent current-extractor requirement',
            'copied_job': 'Append full job text after PROFESSIONAL EXPERIENCE',
            'duplicate': 'Append an identical full resume',
            'equivalent_headings': 'Replace EXPERIENCE and TECHNICAL SKILLS with equivalent headings/spacing',
        },
    })
    cases = []
    for anchor in anchors:
        resume, job = resumes[anchor['resume_id']], jobs[anchor['job_id']]
        requirements = extract_requirements(job, (t for t in VOCAB if t.name.casefold() not in STOP_TERMS))
        missing = [r['term'].name for r in requirements if not _occurrences(r['term'], resume)]
        texts = {
            'baseline': resume,
            'negated_missing': resume + '\n' + '\n'.join(f'I have no experience with {t}.' for t in missing),
            'copied_job': resume + '\nPROFESSIONAL EXPERIENCE\n' + job,
            'duplicate': resume + '\n' + resume,
            'equivalent_headings': resume.replace('\nEXPERIENCE\n', '\nPROFESSIONAL EXPERIENCE\n')
                                        .replace('\nTECHNICAL SKILLS\n', '\nTECHNICAL  SKILLS\n'),
        }
        cases.extend({'id': anchor['id'], 'variant': name, 'resume': text, 'job': job}
                     for name, text in texts.items())
    before = worker(baseline_source, cases)
    after = worker(ROOT / 'src', cases)
    summary = {}
    for phase, observations in (('before', before), ('after', after)):
        baseline = {(r['id'], r['mode']): r['score'] for r in observations
                    if r['variant'] == 'baseline' and 'score' in r}
        groups = defaultdict(list)
        for record in observations:
            if 'score' in record and record['variant'] != 'baseline':
                groups[(record['mode'], record['variant'])].append(
                    record['score'] - baseline[(record['id'], record['mode'])])
        summary[phase] = {
            f'{mode}/{variant}': {'cases': len(deltas), 'increased': sum(d > 0 for d in deltas),
                                 'unchanged': sum(d == 0 for d in deltas),
                                 'max_increase': max(0, max(deltas)), 'min_delta': min(deltas)}
            for (mode, variant), deltas in sorted(groups.items())
        }
    before_base = {(r['id'], r['mode']): r['score'] for r in before if r['variant'] == 'baseline' and 'score' in r}
    preserved = [r['score'] == before_base[(r['id'], r['mode'])] for r in after
                 if r['variant'] == 'baseline' and r['mode'] in ('compatibility', 'legacy_frequency') and 'score' in r]
    result = {'summary': summary, 'observations': {'before': before, 'after': after},
              'calls_per_worker': len(after), 'errors': sum('error' in r for r in before + after),
              'compatibility_legacy_baseline_scores_preserved': {'matched': sum(preserved), 'total': len(preserved)}}
    if (before_hashes != source_hashes(baseline_source) or current_hashes != hashes()
            or digest(Path(__file__).read_bytes()) != runner_hash):
        raise ValueError('Source changed during behavioral comparison')
    for name, expected in manifest['files'].items():
        if digest((corpus / name).read_bytes()) != expected:
            raise ValueError('Corpus changed during comparison')
    write_json(output / 'results.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--baseline-source', type=Path, required=True, help='Baseline src directory in an isolated checkout')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.corpus.resolve(), args.baseline_source.resolve(), args.output)
    print(json.dumps({k: v for k, v in result.items() if k != 'observations'}, indent=2))


if __name__ == '__main__':
    main()
