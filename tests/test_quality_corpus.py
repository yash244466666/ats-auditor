"""Data contract checks only: never score the prospective evaluation corpus."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

path = Path(__file__).parents[1] / "benchmarks/validate_quality_corpus.py"
spec = importlib.util.spec_from_file_location("quality_validator", path)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def test_quality_corpus_references_evidence_and_integrity():
    data = validator.load_corpus()
    validator.verify_hashes(validator.CORPUS, data["manifest"])
    report = validator.validate(data)
    assert report["requirement_labels"] == 288
    assert report["scoring_executed"] is False


def test_rejects_invented_evidence_quote():
    data = deepcopy(validator.load_corpus())
    data["labels"][0]["labels"][0]["evidence"][0]["quote"] = "Unstated invented professional experience."
    with pytest.raises(ValueError, match="quote does not exist"):
        validator.validate(data)


def test_rejects_duplicate_requirement_labels():
    data = deepcopy(validator.load_corpus())
    data["labels"][0]["labels"][1] = deepcopy(data["labels"][0]["labels"][0])
    with pytest.raises(ValueError, match="exactly once"):
        validator.validate(data)


def test_rejects_fabricated_numeric_ground_truth():
    data = deepcopy(validator.load_corpus())
    data["labels"][0]["expected_score"] = 100
    with pytest.raises(ValueError, match="numeric ATS ground truth"):
        validator.validate(data)
