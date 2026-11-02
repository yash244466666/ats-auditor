"""Check the measurement harness with tiny invented inputs, not tuned scores."""
from pathlib import Path
import gzip
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "benchmarks"))
from run_quality_stress import MODES, mutations, summarize, valid_result


def test_existing_repetition_does_not_inject_missing_job_terms():
    text = "SUMMARY\nPython developer.\nEXPERIENCE\nBuilt Python services."
    variants = mutations(text, "Python and Ruby services")
    assert len(variants) == 18
    assert "Ruby" not in variants["existing_terms_50"]
    assert "Ruby" in variants["all_job_terms_50"]
    assert "I have no experience with Ruby." in variants["negated_missing_terms"]


def test_spacing_control_preserves_line_structure():
    text = "SUMMARY\nPython developer\nEXPERIENCE\nBuilt an API.\n"
    changed = mutations(text, "Python API")["horizontal_spaces"]
    assert changed.replace("  ", " ") == text
    assert changed.count("\n") == text.count("\n")


def test_result_contract_rejects_bad_coverage_and_scores():
    result = {"overall_score": 50, "keywords": [{"score": 25}],
              "keyword_coverage": {"matched": 1, "total": 1}}
    assert valid_result(result)
    result["overall_score"] = 101
    assert not valid_result(result)
    result["overall_score"] = 50
    result["keyword_coverage"]["total"] = 2
    assert not valid_result(result)


def test_summary_records_ranking_reversals_instead_of_assuming_correctness():
    anchors = [{"job_id": "j", "resume_id": rid, "relationship": label} for rid, label in
               [("a", "aligned"), ("b", "related"), ("c", "cross_role")]]
    rows = [{"job_id": "j", "resume_id": rid, "mode": mode, "variant": "baseline",
             "score": score, "valid_result": True} for mode in MODES
            for rid, score in [("a", 50), ("b", 60), ("c", 50)]]
    summary = summarize(rows, anchors)
    for mode in MODES:
        assert summary[mode]["ordering"]["aligned_vs_related"]["lower"] == 1
        assert summary[mode]["ordering"]["aligned_vs_cross_role"]["tie"] == 1


def test_recorded_run_artifacts_are_intact_and_denominators_reconcile():
    folder = Path(__file__).parents[1] / "benchmarks/quality_v1_runs/2026-11-03"
    manifest = json.loads((folder / "run_files.json").read_text())
    for filename, expected in manifest.items():
        assert hashlib.sha256((folder / filename).read_bytes()).hexdigest() == expected
    raw = gzip.decompress((folder / "observations.jsonl.gz").read_bytes())
    archive = json.loads((folder / "archive.json").read_text())
    assert hashlib.sha256(raw).hexdigest() == archive["uncompressed_sha256"]
    rows = [json.loads(line) for line in raw.splitlines()]
    summary = json.loads((folder / "summary.json").read_text())
    assert len(rows) == archive["records"] == summary["core_calls"] == 3744
    assert sum(r["variant"] == "baseline" for r in rows) == 576
    assert sum(r["variant"] == "repeat_baseline" for r in rows) == 576
    assert len({(r["job_id"], r["resume_id"]) for r in rows}) == 144
