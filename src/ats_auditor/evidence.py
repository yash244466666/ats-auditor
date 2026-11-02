"""Deterministic evidence guards, deliberately separate from compatibility scoring.

Negation scope and job-text overlap are conservative English heuristics, not
verification of employment or a general semantic entailment model.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

WORDS = re.compile(r"\w+", re.UNICODE)
ACTION = re.compile(r"\b(?:built|developed|designed|implemented|shipped|deployed|optimized|"
                    r"reduced|improved|created|automated|integrated|tested|refactored|secured|"
                    r"debugged|maintained|led|delivered|reviewed|fixed|investigated|wrote|"
                    r"migrated|configured|operated|managed|supported)\b", re.I)
NEGATION = re.compile(r"\b(?:no|not|never|without|lack(?:s|ed|ing)?|unfamiliar|"
                      r"haven't|hasn't|didn't|don't|doesn't|cannot|can't)\b", re.I)
PSEUDO = re.compile(r"\b(?:not only|not just|not without|no problems?|no issues?|"
                    r"without sacrificing|without compromising)\b", re.I)
LEARNING = re.compile(r"\b(?:learning|studying|coursework|tutorials?|training|exploring|"
                       r"beginner|introductory)\b", re.I)
CONTRAST = re.compile(r"\b(?:but|however|whereas|although|while|yet|now)\b|"
                      r"\band\s+(?=(?:built|developed|designed|implemented|deployed)\b)", re.I)
SENTENCE = re.compile(r"(?<=[.!?;])\s+|\n")
POST_NEGATION = re.compile(
    r"^\s*[:(\-–—]*\s*(?:(?:experience|knowledge|skills?|proficiency)\s*)?"
    r"(?:(?:is|was|are|were|has been)\s+)?(?:none\b|never\b|not\b|no\b)", re.I,
)
REQUIREMENT_PROSE = re.compile(r"^(?:you\b|we\s+(?:require|seek|need)|must\b|should\b|"
                               r"required\s*[:\-]|requirements?\s*[:\-])", re.I)


def mention_status(text: str, start: int, end: int, *, job_requirement: bool = False) -> str:
    prefix = SENTENCE.split(text[:start])[-1]
    prefix = CONTRAST.split(prefix)[-1]
    # Bound scope to a short clause while preserving comma-separated skill lists.
    prefix = " ".join(prefix.split()[-16:]).replace("’", "'")
    suffix = SENTENCE.split(text[end:])[0][:100].replace("’", "'")
    if NEGATION.search(PSEUDO.sub("", prefix)) or POST_NEGATION.search(suffix):
        return "negated"
    if job_requirement:
        # 'Python experience is not required' is optional, not a missing skill.
        if re.match(r"^\s*(?:experience\s+)?(?:is\s+)?(?:not required|optional)\b", suffix, re.I):
            return "negated"
        return "claim"
    if LEARNING.search(prefix) or re.match(r"^\s+(?:through|in|via)\s+(?:courses?|tutorials?|training)\b", suffix, re.I):
        return "learning_only"
    return "claim"


def scoped_text(text: str, start: int, end: int) -> str:
    """Keep actions/metrics in a contrasting clause from lending false context."""
    earlier = [m.end() for m in CONTRAST.finditer(text) if m.end() <= start]
    later = [m.start() for m in CONTRAST.finditer(text) if m.start() >= end]
    return text[max(earlier, default=0):min(later, default=len(text))]


def copied_ranges(resume: str, job: str) -> list[tuple[int, int]]:
    """Find normalized shared runs of >=12 words using 8-word shingles.

    Preserve character offsets so copied text cannot erase a separate genuine
    example on the same line. Short common skill lists are not called copies.
    """
    job_words = [m.group().casefold() for m in WORDS.finditer(job)]
    target = {tuple(job_words[i:i + 8]) for i in range(len(job_words) - 7)}
    words = [(m.group().casefold(), m.start(), m.end()) for m in WORDS.finditer(resume)]
    merged: list[list[int]] = []
    for i in range(len(words) - 7):
        if tuple(w[0] for w in words[i:i + 8]) not in target:
            continue
        if merged and i <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], i + 8)
        else:
            merged.append([i, i + 8])
    return [(words[a][1], words[b - 1][2]) for a, b in merged if b - a >= 12]


@dataclass(frozen=True)
class Clause:
    section: str
    text: str
    start: int


@dataclass(frozen=True)
class EvidenceDocument:
    text: str
    clauses: tuple[Clause, ...]
    copied: tuple[tuple[int, int], ...]


def prepare_evidence(resume: str, job: str) -> EvidenceDocument:
    section = "body"
    clauses = []
    cursor = 0
    headings = {
        "experience": "experience", "work experience": "experience", "employment": "experience",
        "professional experience": "experience", "work history": "experience",
        "projects": "projects", "personal projects": "projects", "education": "education",
        "skills": "skills", "technical skills": "skills", "technical capabilities": "skills",
        "relevant technical capabilities": "skills", "summary": "summary", "profile": "summary",
        "certifications": "education", "training": "learning", "courses": "learning",
        "job description": "job_text", "copied job description": "job_text",
        "unverified copied job description": "job_text", "target job": "job_text",
    }
    for raw in resume.splitlines(keepends=True):
        heading = " ".join(raw.strip(" \t\r\n#:•*-").casefold().split())
        if heading in headings:
            section = headings[heading]
        else:
            leading = len(raw) - len(raw.lstrip(" \t•*-"))
            line = raw[leading:].rstrip("\r\n")
            for match in re.finditer(r"\S.*?(?:(?<=[.!?;])(?=\s)|$)", line):
                clauses.append(Clause(section, match.group(), cursor + leading + match.start()))
        cursor += len(raw)
    return EvidenceDocument(resume, tuple(clauses), tuple(copied_ranges(resume, job)))


def assess_keyword(term, document: EvidenceDocument) -> dict:
    from .engine import METRIC_RE
    from .phrases import eligible_occurrences

    raw_count = 0
    accepted = 0
    learning = 0
    skills = 0
    evidence: dict[str, dict] = {}
    excluded = []
    for clause in document.clauses:
        for start, end in eligible_occurrences(term, clause.text):
            raw_count += 1
            absolute = (clause.start + start, clause.start + end)
            copied = clause.section == "job_text" or any(
                absolute[0] < b and a < absolute[1] for a, b in document.copied
            )
            status = ("job_text_overlap" if copied else
                      "requirement_prose" if REQUIREMENT_PROSE.search(clause.text) else
                      mention_status(clause.text, start, end))
            if clause.section == "learning" and status == "claim":
                status = "learning_only"
            if status not in ("claim", "learning_only"):
                excluded.append({"reason": status, "text": " ".join(clause.text.split())[:240]})
                continue
            if status == "learning_only":
                learning += 1
                continue
            accepted += 1
            skill_section = clause.section == "skills"
            skills += int(skill_section)
            local_text = scoped_text(clause.text, start, end)
            if not skill_section and ACTION.search(local_text):
                normalized = " ".join(local_text.split())
                evidence[normalized.casefold()] = {
                    "section": clause.section, "text": normalized[:240],
                    "quantified": bool(METRIC_RE.search(local_text)),
                }
    examples = list(evidence.values())
    if accepted:
        score = 25 + min(25, 15 * len(examples)) + min(25, 15 * sum(e["quantified"] for e in examples))
        score += 10 if len(examples) > 1 else 0
        score += 5 if skills and examples else 0
        status = "contextual" if examples else "self_attested"
    elif learning:
        score, status = 10, "learning_only"
    else:
        score, status = 0, "excluded" if raw_count else "not_found"
    return {
        "keyword": term.name, "present": bool(accepted or learning), "occurrences": raw_count,
        "accepted_mentions": accepted, "learning_mentions": learning,
        "evidence_score": min(100, score), "evidence": examples[:3],
        "status": status, "excluded": excluded[:3],
        "detail": {"contextual": "Action-based example found; employment is not verified.",
                   "self_attested": "Self-attested mention without an action-based example.",
                   "learning_only": "Learning-only mention; delivered work is not established.",
                   "excluded": "Only negated, requirement-like or job-overlap mentions were found.",
                   "not_found": "Not found in supplied resume text."}[status],
    }
