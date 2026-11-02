"""Evaluation correctness tests use fictional sentences, with no network/data download."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))
from evaluate_skillspan import (
    bio_spans, catalog_spans, evaluate, load_split, metrics, novel_sentences, run, validate_row,
)
from ats_auditor.engine import Keyword


def row(tokens, skill, knowledge=None):
    return {"idx": 1, "source": "fictional", "tokens": tokens,
            "tags_skill": skill, "tags_knowledge": knowledge or ["O"] * len(tokens)}


def test_bio_boundaries_and_orphan_policy():
    assert bio_spans(["B", "I", "B", "O", "I"]) == ({(0, 2), (2, 3), (4, 5)}, 1)
    with pytest.raises(ValueError):
        bio_spans(["B-skill"])


@pytest.mark.parametrize("changes", [
    {"tokens": []}, {"tokens": ["two words"]}, {"tags_skill": []},
    {"tags_knowledge": ["X"]}, {"idx": "1"}, {"source": None},
])
def test_rejects_invalid_rows(changes):
    sample = row(["Python"], ["B"])
    sample.update(changes)
    with pytest.raises(ValueError):
        validate_row(sample)


def test_token_boundaries_aliases_and_nested_matches():
    terms = (Keyword("Python"), Keyword("SQL"), Keyword("SQL injection"),
             Keyword("PostgreSQL", ("Postgres",)))
    spans, unaligned = catalog_spans(["Pythonic", "Python", "SQL", "injection", "Postgres"], terms)
    assert spans == {(1, 2), (2, 3), (2, 4), (4, 5)}
    assert unaligned == 0
    # A character-level hit inside one token cannot earn exact-token credit.
    assert catalog_spans(["Python-based"], (Keyword("Python"),)) == (set(), 1)


def test_exact_union_metrics_do_not_double_count_gold_or_predictions():
    samples = [
        row(["Python", "and", "SQL"], ["B", "O", "O"], ["B", "O", "B"]),
        row(["Team", "leadership"], ["B", "I"]),
    ]
    report = evaluate(samples, [Keyword("Python"), Keyword("Python"), Keyword("Team")])
    counts = report["union_exact_span"]
    assert counts == {"true_positive": 1, "false_positive": 1, "false_negative": 2,
                      "precision": 0.5, "recall": 0.333333, "f1": 0.4}
    assert report["skill_span_recall"]["matched"] == 1
    assert report["knowledge_span_recall"]["gold"] == 2
    assert report["document_keys_within_split"] == 1
    assert metrics(0, 0, 0)["f1"] == 0


def test_novel_diagnostic_excludes_earlier_and_internal_repeats_without_mutation():
    old = row(["Python"], ["B"])
    new = row(["Docker"], ["B"])
    repeat = row(["DOCKER"], ["O"])
    samples = [old, new, repeat]
    assert novel_sentences(samples, [old]) == [new]
    assert len(samples) == 3


def test_stale_cache_fails_closed_without_network(tmp_path):
    (tmp_path / "test.jsonl").write_text('{}\n')
    with pytest.raises(ValueError, match="checksum"):
        load_split(tmp_path, "test")
    with pytest.raises(ValueError, match="Missing"):
        load_split(tmp_path, "train")


def test_run_writes_protocol_before_loading_data_and_never_overwrites(tmp_path):
    output = tmp_path / "run"
    with pytest.raises(ValueError, match="Missing"):
        run(tmp_path / "cache", output)
    assert (output / "protocol.json").is_file()
    assert not (output / "results.json").exists()
    with pytest.raises(FileExistsError):
        run(tmp_path / "cache", output)
