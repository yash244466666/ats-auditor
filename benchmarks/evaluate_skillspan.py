"""Offline, exact-span evaluation of existing vocabularies on SkillSpan.

No scoring coefficients are trained. No resume, endpoint, or LLM is involved.
See public_skillspan/README.md for scope, attribution, and metric definitions.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ats_auditor.engine import CATALOG, Keyword, _occurrences
from ats_auditor.requirement_fit import STOP_TERMS, VOCAB
from ats_auditor.source_approx import EXTENDED

SNAPSHOT = "2ccf3de5b5af7a5409b8dd814fb1315dd6e0ae1b"
SHA256 = {
    "train": "5e884c3426087d14fc437d328eb72132082edbfe1e776292ae0e6e9b36c1e1f6",
    "dev": "3732937c6869fe191c749b4efe7ffd597ce84eea1192f09b7fe3bd1eb459e2b4",
    "test": "8438eda34939a5877b984ea5daf9e6ff39b2d5c7e3d73cca0499d3de3784d24a",
}
URL = "https://raw.githubusercontent.com/kris927b/SkillSpan/{}/data/json/{}.json"
MAX_BYTES = 8_000_000
Span = tuple[int, int]  # Token offsets, end exclusive.


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_split(cache: Path, split: str, download: bool = False) -> list[dict]:
    """Load only the pinned JSONL snapshot; reject corrupt/stale cache bytes."""
    path = cache / f"{split}.jsonl"
    if not path.exists():
        if not download:
            raise ValueError(f"Missing {split} cache; use --download to fetch pinned public data")
        with urlopen(URL.format(SNAPSHOT, split), timeout=30) as response:
            data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES or digest(data) != SHA256[split]:
            raise ValueError(f"Downloaded {split} failed size/checksum verification")
        cache.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    data = path.read_bytes()
    if digest(data) != SHA256[split]:
        raise ValueError(f"Cached {split} checksum mismatch; refusing evaluation")
    rows = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    for number, row in enumerate(rows, 1):
        validate_row(row, f"{split}:{number}")
    if not rows:
        raise ValueError(f"Empty {split} split")
    return rows


def validate_row(row: dict, label: str = "row") -> None:
    if not isinstance(row, dict):
        raise ValueError(f"{label}: expected an object")
    tokens = row.get("tokens")
    if not isinstance(tokens, list) or not tokens or any(
        not isinstance(t, str) or not t or any(c.isspace() for c in t) for t in tokens
    ):
        raise ValueError(f"{label}: expected nonempty, whitespace-free tokens")
    if not isinstance(row.get("idx"), int) or not isinstance(row.get("source"), str):
        raise ValueError(f"{label}: invalid document key")
    for field in ("tags_skill", "tags_knowledge"):
        tags = row.get(field)
        if not isinstance(tags, list) or len(tags) != len(tokens) or any(
            t not in ("B", "I", "O") for t in tags
        ):
            raise ValueError(f"{label}: invalid {field}")


def bio_spans(tags: list[str]) -> tuple[set[Span], int]:
    """Treat an orphan I as a new span, explicitly counting this IOB repair."""
    spans: set[Span] = set()
    start = None
    orphan_i = 0
    for index, tag in enumerate([*tags, "O"]):
        if tag not in ("B", "I", "O"):
            raise ValueError("Unexpected BIO tag")
        if tag in ("B", "O") and start is not None:
            spans.add((start, index))
            start = None
        if tag == "B" or (tag == "I" and start is None):
            orphan_i += int(tag == "I")
            start = index
    return spans, orphan_i


def catalog_spans(tokens: list[str], terms: Iterable[Keyword]) -> tuple[set[Span], int]:
    """Scan uncapped catalogs on space-joined tokens, retaining nested matches.

    Only token-aligned matches are eligible for span metrics. This adapter
    deliberately does not learn detokenization or category labels from gold.
    """
    text = " ".join(tokens)
    starts, ends = {}, {}
    offset = 0
    for index, token in enumerate(tokens):
        starts[offset] = index
        ends[offset + len(token)] = index + 1
        offset += len(token) + 1
    spans: set[Span] = set()
    unaligned: set[Span] = set()
    for term in terms:
        for start, end in _occurrences(term, text):
            if start in starts and end in ends:
                spans.add((starts[start], ends[end]))
            else:
                unaligned.add((start, end))
    return spans, len(unaligned)


def catalogs() -> dict[str, tuple[Keyword, ...]]:
    return {
        "evidence_catalog": CATALOG,
        "compatibility_catalog": (*CATALOG, *EXTENDED),
        "requirement_fit_catalog": tuple(t for t in VOCAB if t.name.casefold() not in STOP_TERMS),
    }


def sentence_key(row: dict) -> str:
    return " ".join(row["tokens"]).casefold()


def metrics(tp: int, fp: int, fn: int) -> dict[str, Any]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "true_positive": tp, "false_positive": fp, "false_negative": fn,
        "precision": round(precision, 6), "recall": round(recall, 6),
        "f1": round(2 * tp / (2 * tp + fp + fn), 6) if 2 * tp + fp + fn else 0.0,
    }


def evaluate(rows: list[dict], terms: Iterable[Keyword]) -> dict:
    totals: Counter = Counter()
    terms = tuple(terms)
    for row in rows:
        predicted, unaligned = catalog_spans(row["tokens"], terms)
        skill, skill_orphans = bio_spans(row["tags_skill"])
        knowledge, knowledge_orphans = bio_spans(row["tags_knowledge"])
        gold = skill | knowledge
        totals.update({"tp": len(predicted & gold), "fp": len(predicted - gold),
                       "fn": len(gold - predicted), "skill_gold": len(skill),
                       "skill_hit": len(skill & predicted), "knowledge_gold": len(knowledge),
                       "knowledge_hit": len(knowledge & predicted), "unaligned": unaligned,
                       "orphan_i": skill_orphans + knowledge_orphans})
    return {
        "sentences": len(rows),
        "document_keys_within_split": len({(r["source"], r["idx"]) for r in rows}),
        "union_exact_span": metrics(totals["tp"], totals["fp"], totals["fn"]),
        # Predictions are untyped: category precision/F1 would be misleading.
        "skill_span_recall": {
            "matched": totals["skill_hit"], "gold": totals["skill_gold"],
            "recall": round(totals["skill_hit"] / totals["skill_gold"], 6) if totals["skill_gold"] else 0.0,
        },
        "knowledge_span_recall": {
            "matched": totals["knowledge_hit"], "gold": totals["knowledge_gold"],
            "recall": round(totals["knowledge_hit"] / totals["knowledge_gold"], 6) if totals["knowledge_gold"] else 0.0,
        },
        "unaligned_character_matches_excluded": totals["unaligned"],
        "orphan_i_starts_treated_as_b": totals["orphan_i"],
    }


def audit(splits: dict[str, list[dict]]) -> dict:
    keys = {name: {sentence_key(r) for r in rows} for name, rows in splits.items()}
    return {
        "splits": {
            name: {
                "sentences": len(rows), "sources": dict(Counter(r["source"] for r in rows)),
                "document_keys_within_split": len({(r["source"], r["idx"]) for r in rows}),
                "duplicate_normalized_sentence_rows": len(rows) - len(keys[name]),
                "orphan_i_starts": sum(bio_spans(r[f])[1] for r in rows
                                       for f in ("tags_skill", "tags_knowledge")),
            } for name, rows in splits.items()
        },
        "normalized_unique_sentence_intersections": {
            f"{a}_{b}": len(keys[a] & keys[b])
            for a, b in (("train", "dev"), ("train", "test"), ("dev", "test"))
        },
    }


def novel_sentences(rows: list[dict], earlier: list[dict]) -> list[dict]:
    """A diagnostic only; preserve official splits in the primary result."""
    seen = {sentence_key(r) for r in earlier}
    result = []
    for row in rows:
        key = sentence_key(row)
        if key not in seen:
            result.append(row)
            seen.add(key)
    return result


def source_hashes() -> dict[str, str]:
    paths = [Path(__file__), *(ROOT / "src/ats_auditor" / p for p in
              ("engine.py", "source_approx.py", "requirement_fit.py"))]
    return {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in paths}


def revision() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(cache: Path, output: Path, download: bool = False) -> dict:
    # No overwrite of historical protocols/results, even when a prior run failed.
    output.mkdir(parents=True, exist_ok=False)
    hashes = source_hashes()
    protocol = {
        "schema_version": 1, "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": revision(), "python": sys.version.split()[0],
        "source_sha256": hashes, "dataset_commit": SNAPSHOT,
        "dataset_sha256": SHA256, "dataset_urls": {s: URL.format(SNAPSHOT, s) for s in SHA256},
        "dataset_license_card": "https://huggingface.co/datasets/jjzha/skillspan/blob/main/README.md",
        "method": "Uncapped existing vocabularies; exact token-aligned spans against skill/knowledge union; untyped predictions",
        "orphan_i_policy": "Treat I after O as B and count; preserve raw files",
        "primary_split": "test", "official_splits_preserved": True,
        "diagnostic": "First unique normalized test sentence absent from both train and dev",
        "training_or_coefficient_tuning": False, "resume_fit_or_hiring_accuracy": False,
    }
    write_json(output / "protocol.json", protocol)
    splits = {s: load_split(cache, s, download) for s in SHA256}
    views = {
        **splits,
        "test_unique_absent_train_dev": novel_sentences(splits["test"], splits["train"] + splits["dev"]),
    }
    result = {
        "schema_version": 1, "audit": audit(splits),
        "evaluations": {name: {view: evaluate(rows, terms) for view, rows in views.items()}
                        for name, terms in catalogs().items()},
        "test_by_source": {name: {source: evaluate([r for r in splits["test"] if r["source"] == source], terms)
                                  for source in sorted({r["source"] for r in splits["test"]})}
                           for name, terms in catalogs().items()},
    }
    if hashes != source_hashes():
        raise ValueError("Source changed during evaluation; discard incomplete run")
    for split in SHA256:
        if digest((cache / f"{split}.jsonl").read_bytes()) != SHA256[split]:
            raise ValueError("Dataset changed during evaluation; discard incomplete run")
    write_json(output / "results.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=ROOT / "benchmarks/.cache/skillspan")
    parser.add_argument("--output", type=Path, required=True, help="New run directory; never overwritten")
    parser.add_argument("--download", action="store_true", help="Fetch pinned public job annotations if absent")
    args = parser.parse_args()
    result = run(args.cache, args.output, args.download)
    print(json.dumps({name: views["test"]["union_exact_span"]
                      for name, views in result["evaluations"].items()}, indent=2))


if __name__ == "__main__":
    main()
