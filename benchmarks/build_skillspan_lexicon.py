"""Build a small phrase lexicon from pinned SkillSpan training annotations only."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import unicodedata

from evaluate_skillspan import ROOT, SHA256, SNAPSHOT, bio_spans, load_split
from ats_auditor.phrases import PhraseMatcher, tokenize

# Fixed training-only rules; no test labels are used to select entries.
MIN_DOCUMENTS = 2
MIN_TRAIN_PRECISION = 0.8
MAX_TOKENS = 12


def build(rows: list[dict]) -> dict:
    documents = defaultdict(set)
    prepared = []
    for row in rows:
        text = " ".join(row["tokens"])
        offsets, cursor = [], 0
        for token in row["tokens"]:
            offsets.append((cursor, cursor + len(token)))
            cursor += len(token) + 1
        gold = set()
        spans = bio_spans(row["tags_skill"])[0] | bio_spans(row["tags_knowledge"])[0]
        for start, end in spans:
            a, b = offsets[start][0], offsets[end - 1][1]
            phrase = " ".join(t for t, _, _ in tokenize(text[a:b]))
            phrase = re.sub(r"\s*([.+/#-])\s*", r"\1", phrase)
            if (not phrase or "<" in phrase or ">" in phrase or
                    any(unicodedata.category(c).startswith('C') for c in phrase) or
                    re.search(r"\\\s*x\s*[0-9a-f]{2}", phrase, re.I) or
                    any(phrase.count(a) != phrase.count(b) for a, b in (("(", ")"), ("[", "]"))) or
                    not re.search(r"[\w+#]$", phrase) or
                    len(tokenize(phrase)) > MAX_TOKENS or not any(c.isalpha() for c in phrase)):
                continue
            documents[phrase].add((row["source"], row["idx"]))
            gold.add((a, b))
        prepared.append((text, gold))
    candidates = [phrase for phrase, docs in documents.items() if len(docs) >= MIN_DOCUMENTS]
    matcher = PhraseMatcher(candidates)
    counts, correct = Counter(), Counter()
    for text, gold in prepared:
        for hit in matcher.find(text, longest_only=False):
            counts[hit.name] += 1
            correct[hit.name] += (hit.start, hit.end) in gold
    phrases = sorted(p for p in candidates if correct[p] / counts[p] >= MIN_TRAIN_PRECISION)
    return {
        "schema_version": 1,
        "source": "SkillSpan: Zhang, Jensen, Sonniks and Plank (NAACL 2022)",
        "source_url": "https://github.com/kris927b/SkillSpan",
        "dataset_commit": SNAPSHOT, "training_sha256": SHA256["train"],
        "split_used": "train", "license": "CC-BY-4.0",
        "license_card": "https://huggingface.co/datasets/jjzha/skillspan/blob/main/README.md",
        "rules": {"min_distinct_training_documents": MIN_DOCUMENTS,
                  "min_training_exact_span_precision": MIN_TRAIN_PRECISION,
                  "max_normalized_tokens": MAX_TOKENS},
        "phrases": phrases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=ROOT / "benchmarks/.cache/skillspan")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(load_split(args.cache, "train"))
    # Never silently replace an already published data artifact.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"Built {len(result['phrases'])} phrases from training annotations only")


if __name__ == "__main__":
    main()
