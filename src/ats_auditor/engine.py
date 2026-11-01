"""Independent ATS scoring engine.

Compatibility mode approximates the *observed* Upplai tool interface and
frequency-sensitive behavior. It does not reproduce proprietary code.
Evidence mode is a more conservative screening heuristic, intended to resist
keyword stuffing. Neither mode predicts a real employer's ATS decision.
"""
from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass
from collections import Counter
from typing import Any


@dataclass(frozen=True)
class Keyword:
    name: str
    aliases: tuple[str, ...] = ()


# Preferred labels and aliases. Exact word/phrase boundaries are enforced below.
CATALOG: tuple[Keyword, ...] = (
    Keyword("AI", ("artificial intelligence",)),
    Keyword("full-stack", ("full stack", "fullstack")),
    Keyword("React", ("React.js",)),
    Keyword("TypeScript", ("TS",)),
    Keyword("Python"),
    Keyword("databases", ("database",)),
    Keyword("LangGraph"),
    Keyword("LangChain"),
    Keyword("OpenAI", ("OpenAI API",)),
    Keyword("pytest"),
    Keyword("Playwright"),
    Keyword("Testing Library", ("React Testing Library",)),
    Keyword("Vitest"),
    Keyword("Redis"),
    Keyword("SQLAlchemy"),
    Keyword("PostgreSQL", ("Postgres",)),
    Keyword("FastAPI"),
    Keyword("caching", ("cache", "cached")),
    Keyword("state management", ("state-management",)),
    Keyword("authentication", ("authorization", "authn", "JWT", "Auth0")),
    Keyword("Next.js", ("NextJS",)),
    Keyword("Node.js", ("NodeJS",)),
    Keyword("GraphQL"),
    Keyword("Relay"),
    Keyword("Zustand"),
    Keyword("Tailwind CSS", ("Tailwind",)),
    Keyword("shadcn/ui", ("shadcn",)),
    Keyword("Radix UI", ("Radix",)),
    Keyword("Strawberry GraphQL", ("Strawberry",)),
    Keyword("Alembic"),
    Keyword("ARQ"),
    Keyword("REST API", ("RESTful APIs", "REST APIs", "RESTful API")),
    Keyword("Docker"),
    Keyword("CI/CD", ("continuous integration", "continuous delivery")),
    Keyword("GitHub Actions"),
    Keyword("security"),
    Keyword("TDD", ("test-driven development",)),
    Keyword("unit testing", ("unit tests",)),
    Keyword("integration testing", ("integration tests",)),
    Keyword("code review", ("code reviews",)),
    Keyword("performance", ("performance optimization",)),
    Keyword("bug fixing", ("bug fixes", "debugging", "bugs")),
    Keyword("MCP", ("Model Context Protocol",)),
    Keyword("Django"),
    Keyword("Ruby on Rails", ("Rails",)),
    Keyword("MongoDB"),
    Keyword("MySQL"),
    Keyword("Express.js", ("ExpressJS",)),
    Keyword("NestJS", ("Nest.js",)),
    Keyword("JavaScript", ("JS",)),
    Keyword("C#"),
    Keyword("Vue.js", ("Vue",)),
    Keyword("Redux"),
    Keyword("Agile", ("Scrum",)),
)

ACTION_RE = re.compile(r"\b(?:built|build|developed|designed|implemented|shipped|deployed|optimized|"
                       r"reduced|improved|created|automated|integrated|tested|refactored|"
                       r"secured|debugged|maintained|led|delivered|reviewed|fixed|"
                       r"investigated|wrote|migrated|configured|operated)\b", re.I)
METRIC_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|percent|ms|seconds?|hours?|users?|requests?|x|×)\b", re.I)
HEADING_RE = re.compile(r"^(?:SUMMARY|PROFILE|SKILLS|TECHNICAL SKILLS|EXPERIENCE|WORK EXPERIENCE|"
                        r"EMPLOYMENT|PROJECTS|EDUCATION|RELEVANT TECHNICAL CAPABILITIES|"
                        r"CERTIFICATIONS|AI & DELIVERY|FRONTEND|BACKEND)\s*:?$", re.I)


def _pattern(phrase: str) -> re.Pattern[str]:
    body = re.escape(phrase).replace(r"\ ", r"\s+")
    # Prevent matching "AI" as part of "OpenAI" or "Rails" as part of another word.
    return re.compile(r"(?<![A-Za-z0-9])" + body + r"(?![A-Za-z0-9])", re.I)


def _occurrences(term: Keyword, text: str) -> list[tuple[int, int]]:
    spans: set[tuple[int, int]] = set()
    for alias in (term.name, *term.aliases):
        # Avoid treating "TS" and "JS" common English words accidentally.
        if alias in {"TS", "JS"}:
            continue
        spans.update((m.start(), m.end()) for m in _pattern(alias).finditer(text))
    # Collapse nested aliases, e.g. "React Testing Library" and "Testing Library".
    hits: list[tuple[int, int]] = []
    for a, b in sorted(spans, key=lambda ab: (ab[0], -(ab[1] - ab[0]))):
        if not any(x <= a and b <= y for x, y in hits):
            hits.append((a, b))
    return hits


def _sectioned_lines(text: str) -> list[tuple[str, str]]:
    section = "body"
    result = []
    for raw in text.splitlines():
        line = raw.strip(" \t•-*\u2022")
        if HEADING_RE.fullmatch(line):
            section = line.casefold()
        elif line:
            result.append((section, line))
    return result


def _importance(term: Keyword, job_text: str, job_count: int) -> str:
    if job_count >= 4:
        return "very high"
    if job_count >= 3:
        return "high"
    if job_count >= 2:
        return "medium"
    return "low"


def extract_keywords(job_text: str, max_keywords: int = 25) -> list[dict[str, Any]]:
    """Extract job-specific terms, not keywords absent from the job description.

    The initial catalog order is tuned to common software-engineering JDs.
    In a real recruitment setting, employer requirements and human review
    must override catalog heuristics.
    """
    found = []
    for term in CATALOG:
        n = len(_occurrences(term, job_text))
        if n:
            found.append({"term": term, "job_mentions": n,
                          "importance": _importance(term, job_text, n)})
    # Preserve stable catalog order, with job frequency/importance priority for long JDs.
    if len(found) > max_keywords:
        found = sorted(found, key=lambda k: (-k["job_mentions"], CATALOG.index(k["term"])))[:max_keywords]
    return found


def _round(value: float) -> int:
    return max(0, min(100, int(math.floor(value + 0.5))))


def _weight(importance: str) -> float:
    return {"very high": 5.5, "high": 3.0, "medium": 1.8, "low": 1.0}[importance]


def keyword_scores(term: Keyword, importance: str, resume_text: str) -> dict[str, Any]:
    hits = _occurrences(term, resume_text)
    lines = _sectioned_lines(resume_text)
    evidence = []
    n_in_skills = 0
    n_context = 0
    context_hits = 0
    for section, line in lines:
        count = len(_occurrences(term, line))
        if not count:
            continue
        skill_section = ("skill" in section or "capabilities" in section) or line.lower().startswith(("front-end:", "back-end:", "databases:", "testing &", "ai & delivery:"))
        # A capabilities section counts as evidence of familiarity, but not job-specific impact.
        relevant_context = not skill_section
        n_in_skills += count if skill_section else 0
        n_context += count if relevant_context else 0
        act = bool(ACTION_RE.search(line))
        metric = bool(METRIC_RE.search(line))
        if act and relevant_context:
            context_hits += 1
        if (act or metric) and relevant_context:
            evidence.append({"section": section, "text": line[:240], "quantified": metric})
    n = len(hits)
    if n == 0:
        return {"keyword": term.name, "present": False, "importance": importance,
                "score": 0, "evidence_score": 0, "occurrences": 0, "evidence": [],
                "detail": "Not found in supplied resume text."}

    # Compatibility heuristic: frequency-sensitive, in the same qualitative
    # direction as the observed third-party API; *not* a cloned formula.
    if term.name == "AI":
        compat = _round(21 + 2.3 * n + min(10, 2 * context_hits))
    else:
        compat = _round(34 + 21 * max(0, n - 1) + min(18, 6 * context_hits)
                        + min(10, 4 * sum(1 for e in evidence if e["quantified"])))
    compat = min(100, compat)

    # Recruiter-oriented evidence mode: repeated word lists don't count as
    # proof of professional capability. Repetition gives limited credit.
    contextual_lines = len({e["text"] for e in evidence})
    quantified_lines = sum(1 for e in evidence if e["quantified"])
    evidence_score = 25 + min(25, 15 * contextual_lines) + min(25, 15 * quantified_lines)
    evidence_score += 10 if contextual_lines > 1 else 0
    if n_in_skills and contextual_lines:
        evidence_score += 5
    evidence_score = min(100, evidence_score)
    if n > 10 and contextual_lines == 0:
        evidence_score = min(25, evidence_score)

    return {"keyword": term.name, "present": True, "importance": importance,
            "score": compat, "evidence_score": int(evidence_score), "occurrences": n,
            "evidence": evidence[:3],
            "detail": "Context evidence found" if contextual_lines else "Appears in text without an action-based example"}


def _formatting_checks(text: str) -> list[str]:
    warnings = []
    if not re.search(r"[\w.+-]+@[\w.-]+\.\w+", text):
        warnings.append("No email address detected in plain text.")
    if not re.search(r"(?im)^\s*(?:experience|work experience|employment)\s*$", text):
        warnings.append("No separate Experience heading detected.")
    if len(text.split()) < 150:
        warnings.append("Resume appears unusually short; provide the complete document.")
    if text.count("\t") >= 10:
        warnings.append("Many tabs detected; confirm the layout remains readable after ATS text extraction.")
    if text.count("|") > 16:
        warnings.append("Pipe-separated content may not remain readable in all ATS parsers.")
    warnings.append("Text-only analysis cannot verify embedded images, columns, headers, footers, or actual PDF parsing.")
    return warnings


def _stuffing_signals(text: str, metrics: list[dict[str, Any]]) -> list[str]:
    warnings = []
    words = max(1, len(text.split()))
    for k in metrics:
        if k["occurrences"] >= 12 and k["occurrences"] / words >= 0.013:
            warnings.append(f"Potential keyword saturation: {k['keyword']} appears {k['occurrences']} times.")
    repeated = Counter(line.strip() for line in text.splitlines() if len(line.strip()) > 70)
    if any(n >= 3 for n in repeated.values()):
        warnings.append("Identical long lines are repeated at least three times.")
    return warnings[:8]


def score_resume(resume_text: str, job_description: str, mode: str = "compatibility",
                 max_keywords: int = 20) -> dict[str, Any]:
    if mode not in {"compatibility", "evidence", "legacy_frequency", "requirement_fit"}:
        raise ValueError("mode must be compatibility, evidence, legacy_frequency, or requirement_fit")
    if not resume_text.strip() or not job_description.strip():
        raise ValueError("Full resume_text and job_description are required")
    if len(resume_text.strip()) < 100 or len(job_description.strip()) < 50:
        raise ValueError("The input appears incomplete; provide the full resume and job description")
    if mode == "requirement_fit":
        from .requirement_fit import role_fit_score
        return role_fit_score(resume_text, job_description)
    if mode == "compatibility":
        # Broader, black-box calibrated matcher. The old frequency-sensitive
        # behavior remains separately available as `legacy_frequency` for
        # reproducibility of earlier experiments.
        from .source_approx import score_source_approx
        output = score_source_approx(resume_text, job_description)
        simple_metrics = [
            {"keyword":k["keyword"], "occurrences":k["resume_mentions"]}
            for k in output["details"]["keyword_counts"]
        ]
        stuffing = _stuffing_signals(resume_text, simple_metrics)
        output["details"].update({
            "format_warnings": _formatting_checks(resume_text),
            "keyword_stuffing_warnings": stuffing,
            "recommendations": [f"Provide verifiable project evidence for {k['keyword']}."
                                for k in output["keywords"] if not k["present"]][:8],
        })
        return output
    discovered = extract_keywords(job_description, max_keywords=max_keywords)
    if not discovered:
        raise ValueError("No supported job keywords found; extend the catalog for this field")
    metrics = [keyword_scores(k["term"], k["importance"], resume_text) for k in discovered]
    weights = [_weight(x["importance"]) for x in metrics]
    scoring_key = "evidence_score" if mode == "evidence" else "score"
    raw = sum(m[scoring_key] * w for m, w in zip(metrics, weights)) / sum(weights)
    stuffing = _stuffing_signals(resume_text, metrics)
    # Preserve the experimental compatibility behavior, but apply a penalty
    # to the evidence-oriented result to discourage ATS gaming.
    if mode == "evidence" and stuffing:
        raw -= min(25, 8 * len(stuffing))
    overall = _round(raw)
    return {
        "overall_score": overall,
        "keyword_coverage": {"matched": sum(m["present"] for m in metrics), "total": len(metrics)},
        "keywords": [{"keyword": m["keyword"], "present": m["present"],
                      "importance": m["importance"], "score": m[scoring_key]} for m in metrics],
        "details": {"mode": mode,
                    "scoring_method": "original frequency-sensitive heuristic (legacy)" if mode == "legacy_frequency" else "independent contextual evidence heuristic",
                    "keyword_evidence": [{"keyword": m["keyword"], "occurrences": m["occurrences"],
                                          "evidence": m["evidence"], "note": m["detail"]} for m in metrics],
                    "format_warnings": _formatting_checks(resume_text),
                    "keyword_stuffing_warnings": stuffing,
                    "recommendations": [f"Show a genuine project example demonstrating {m['keyword']}."
                                        for m in metrics if not m["present"] or m["evidence_score"] < 65][:8],
                    "limitations": ["Not an official ATS score or prediction of a hiring decision.",
                                    "Upplai's private internal implementation is not available.",
                                    "Plain text cannot verify document layout, file corruption or ATS-specific parsing."]},
    }
