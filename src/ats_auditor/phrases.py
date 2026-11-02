"""Small local phrase lexicon and shared requirement extraction.

The bundled lexicon is derived from SkillSpan TRAIN ONLY (CC BY 4.0).
Code is MIT; see data/SKILLSPAN_NOTICE.md for the separate data notice.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
import json
import re
from typing import Iterable

TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)
ELIGIBILITY_RE = re.compile(r"\b(?:work authori[sz]ation|authori[sz]ed to work|right to work)\b", re.I)


def tokenize(text: str) -> list[tuple[str, int, int]]:
    return [(m.group().casefold(), m.start(), m.end()) for m in TOKEN_RE.finditer(text)]


@dataclass(frozen=True)
class PhraseHit:
    name: str
    start: int
    end: int


class PhraseMatcher:
    def __init__(self, phrases: Iterable[str]) -> None:
        self.trie: dict = {}
        for phrase in sorted(set(phrases)):
            node = self.trie
            for token, _, _ in tokenize(phrase):
                node = node.setdefault(token, {})
            node[None] = phrase

    def find(self, text: str, *, longest_only: bool = True) -> list[PhraseHit]:
        tokens = tokenize(text)
        hits = []
        i = 0
        while i < len(tokens):
            node = self.trie
            matches = []
            j = i
            while j < len(tokens) and tokens[j][0] in node:
                node = node[tokens[j][0]]
                if None in node:
                    matches.append((j, PhraseHit(node[None], tokens[i][1], tokens[j][2])))
                j += 1
            if matches and longest_only:
                j, match = matches[-1]
                hits.append(match)
                i = j + 1
            else:
                hits.extend(hit for _, hit in matches)
                i += 1
        return hits


@lru_cache(maxsize=1)
def lexicon() -> dict:
    return json.loads(files("ats_auditor").joinpath("data/skillspan_phrases.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def phrase_matcher() -> PhraseMatcher:
    return PhraseMatcher(lexicon()["phrases"])


def eligible_occurrences(term, text: str) -> list[tuple[int, int]]:
    """Do not mistake work authorization for technical authorization."""
    from .engine import _occurrences

    blocked = [(m.start(), m.end()) for m in ELIGIBILITY_RE.finditer(text)]
    return [(a, b) for a, b in _occurrences(term, text)
            if not any(a < y and x < b for x, y in blocked)]


def extract_requirements(job: str, vocabulary: Iterable, max_terms: int = 80) -> list[dict]:
    """Merge existing aliases and training phrases; retain origins, dedupe spans.

    This is lexical requirement detection, not a full obligation/eligibility parser.
    Explicitly denied/not-required job terms are excluded via shared scope rules.
    """
    from .engine import Keyword, _importance
    from .evidence import mention_status

    candidates: dict[str, dict] = {}
    occupied: list[tuple[int, int]] = []
    for term in vocabulary:
        hits = [(a, b) for a, b in eligible_occurrences(term, job)
                if mention_status(job, a, b, job_requirement=True) != "negated"]
        if hits:
            candidates[term.name.casefold()] = {"term": term, "spans": hits, "origin": "catalog"}
            occupied.extend(hits)
    for hit in phrase_matcher().find(job):
        if mention_status(job, hit.start, hit.end, job_requirement=True) == "negated":
            continue
        key = hit.name.casefold()
        if key in candidates:
            if candidates[key]["origin"] == "skillspan_train":
                candidates[key]["spans"].append((hit.start, hit.end))
            continue
        if any(a <= hit.start and hit.end <= b for a, b in occupied):
            continue
        # If the training lexicon knows a longer phrase, prefer it to fragments.
        for name, candidate in list(candidates.items()):
            remaining = [(a, b) for a, b in candidate["spans"]
                         if not (hit.start <= a and b <= hit.end)]
            if not remaining:
                del candidates[name]
            else:
                candidate["spans"] = remaining
        candidate = candidates.setdefault(key, {
            "term": Keyword(hit.name, (job[hit.start:hit.end],)), "spans": [], "origin": "skillspan_train",
        })
        candidate["spans"].append((hit.start, hit.end))
    rows = []
    for item in candidates.values():
        n = len(set(item["spans"]))
        rows.append({**item, "job_mentions": n, "importance": _importance(item["term"], job, n)})
    rows.sort(key=lambda r: (-r["job_mentions"], r["spans"][0][0], -len(r["term"].name)))
    return rows[:max_terms]
