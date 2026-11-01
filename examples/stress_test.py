"""Demonstrate the *failure mode* of frequency-sensitive ATS scoring.

THIS IS NOT A RESUME AND MUST NOT BE USED FOR A REAL JOB APPLICATION.
"""
from pathlib import Path
from ats_auditor.engine import score_resume, extract_keywords

folder = Path(__file__).parent
jd = (folder / 'truey_job.txt').read_text(encoding='utf-8')
base = (folder / 'synthetic_resume.txt').read_text(encoding='utf-8')
keywords = [x['term'].name for x in extract_keywords(jd, max_keywords=20)]
artificial = base + '\nEXPERIMENTAL KEYWORD FREQUENCY STRESS TEST (NOT A REAL RESUME)\n' + (
    ' '.join(keywords) + '\n') * 45
frequency_result = score_resume(artificial, jd, mode='compatibility')
evidence_result = score_resume(artificial, jd, mode='evidence')
print('Synthetic frequency-sensitive score:', frequency_result['overall_score'])
print('Synthetic evidence-based score:', evidence_result['overall_score'])
print('Keyword-stuffing warnings:', frequency_result['details']['keyword_stuffing_warnings'])
