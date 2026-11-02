"""Validate curated data without importing or running a scoring engine.

Run from any directory: python benchmarks/validate_quality_corpus.py
Checks are structural/curatorial; they do not independently adjudicate labels.
"""
from __future__ import annotations

import ast
from collections import Counter
from datetime import date
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "benchmarks" / "quality_v1"
FAMILIES = {"backend", "frontend", "fullstack", "security", "infrastructure", "data"}
PAYLOADS = ("sources.json", "resumes.json", "jobs.json", "labels.json")


def normalized(text: str) -> str:
    return " ".join(re.findall(r"\w+", text.casefold()))


def load_corpus(folder: Path = CORPUS) -> dict[str, Any]:
    return {name.removesuffix(".json"): json.loads((folder / name).read_text())
            for name in (*PAYLOADS, "manifest.json")}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def index(rows: list[dict], name: str) -> dict[str, dict]:
    result = {row["id"]: row for row in rows}
    require(len(result) == len(rows), f"Duplicate {name} IDs")
    return result


def validate(data: dict[str, Any]) -> dict[str, Any]:
    """Validate cross-file IDs, complete annotation coverage and real quotes."""
    resumes = index(data["resumes"], "resume")
    jobs = index(data["jobs"], "job")
    sources = index(data["sources"], "source")
    pairs = index(data["labels"], "pair")
    require(len(resumes) == 12 and len(jobs) == 12 and len(pairs) == 36,
            "quality-v1 requires 12 resumes, 12 jobs and 36 anchor pairs")
    require(data["manifest"]["scoring_status_at_freeze"] == "not_run_on_this_corpus",
            "Keep the historical pre-scoring freeze record; record later runs separately")
    require(data["manifest"]["external_provider_scores_available"] is False,
            "No external provider ground truth exists for quality-v1")
    for group, name, minimum in [(resumes, "resume", 300), (jobs, "job", 190)]:
        require(Counter(x["family"] for x in group.values()) == Counter({f: 2 for f in FAMILIES}),
                f"Expected two {name} records per family")
        texts = [normalized(x["text"]) for x in group.values()]
        require(len(set(texts)) == len(texts), f"Duplicate normalized {name} text")
        for i, text in enumerate(texts):
            for other in texts[i+1:]:
                require(SequenceMatcher(None, text.split(), other.split(), autojunk=False).ratio() < .8,
                        f"Near-duplicate {name} text needs review")
        for record in group.values():
            require(record["fictional"] is True and "FICTIONAL" in record["text"],
                    f"Missing fictional marker: {record['id']}")
            require(len(record["text"].split()) >= minimum,
                    f"Incomplete {name}: {record['id']}")
            require(record["review_status"] == "author_reviewed_pending_independent_review",
                    "Do not imply independent review")
            require(not re.search(r"https?://", record["text"]),
                    "Keep source URLs in metadata, outside scored text")
    for resume in resumes.values():
        for heading in ("SUMMARY", "TECHNICAL SKILLS", "EXPERIENCE", "PROJECTS", "EDUCATION", "SCOPE NOTES"):
            require(f"\n{heading}\n" in resume["text"], f"Missing {heading}: {resume['id']}")
        emails = re.findall(r"[\w.+-]+@[\w.-]+", resume["text"])
        require(emails and all(x.endswith("@example.test") for x in emails),
                "Only reserved example.test contacts are allowed")
        require(date.fromisoformat(resume["career_start"] + "-01") < date.fromisoformat(resume["as_of"]),
                "Career start must precede snapshot")
        periods = re.findall(r"(\d{4}-\d{2}) to (\d{4}-\d{2})", resume["text"])
        require(len(periods) == 2, "Two employment/placement periods expected")
        for start, end in periods:
            require(resume["career_start"] <= start <= end <= resume["as_of"][:7],
                    f"Invalid employment period: {resume['id']}")
    for source in sources.values():
        require(source["status"] == 200 and source["resolved_url"].startswith("https://"),
                "Source was not successfully retrieved")
        require(source["license"] in {"CC-BY-SA-4.0", "OGL-UK-3.0"}, "Source license missing")
        require(bool(re.fullmatch(r"[0-9a-f]{64}", source["sha256"])), "Invalid retrieval hash")
        require(source["retrieved_on"] == "2026-11-02", "Missing dated provenance")
    for job in jobs.values():
        require(job["source_ids"] and set(job["source_ids"]) <= sources.keys(), "Unknown source ID")
        reqs = index(job["requirements"], "requirement")
        require(len(reqs) == 8, "Eight requirements expected")
        require(Counter(q["priority"] for q in reqs.values()) == {"required": 6, "preferred": 2},
                "Required and preferred criteria must stay separate")
        for q in reqs.values():
            require(q["text"] in job["text"], f"Requirement missing from job text: {q['id']}")
        require(set(job["eligibility"].values()) == {"unspecified"}, "Eligibility is not established")
    relationships = Counter()
    statuses = Counter()
    seen_pairs = set()
    for pair in pairs.values():
        key = (pair["job_id"], pair["resume_id"])
        require(key not in seen_pairs, "Repeated job/resume pair")
        seen_pairs.add(key)
        require(key[0] in jobs and key[1] in resumes, "Orphan pair reference")
        job, resume = jobs[key[0]], resumes[key[1]]
        require(pair["expected_score"] is None, "Do not invent numeric ATS ground truth")
        require(pair["review_status"] == "author_reviewed_pending_independent_review",
                "Label review status missing")
        relationships[pair["relationship"]] += 1
        label_ids = [x["requirement_id"] for x in pair["labels"]]
        require(set(label_ids) == {x["id"] for x in job["requirements"]} and len(label_ids) == 8,
                "Every pair must annotate every requirement exactly once")
        for label in pair["labels"]:
            status = label["status"]
            require(status in {"contextual", "partial", "learning_only", "not_evidenced"}, "Unknown evidence status")
            statuses[status] += 1
            require(bool(label["evidence"]) == (status != "not_evidenced"), "Evidence/status mismatch")
            require(bool(label["rationale"]), "Label rationale missing")
            for evidence in label["evidence"]:
                require(evidence["quote"] in resume["text"], "Evidence quote does not exist in resume")
                section = evidence["section"]
                require(f"\n{section}\n" in resume["text"], "Unknown evidence section")
                section_text = resume["text"].split(f"\n{section}\n", 1)[1].split("\n\n", 1)[0]
                require(evidence["quote"] in section_text, "Evidence quote is outside its stated section")
    require(relationships == {"aligned": 12, "related": 12, "cross_role": 12}, "Pair coverage incomplete")
    for jid in jobs:
        require({p["relationship"] for p in pairs.values() if p["job_id"] == jid}
                == {"aligned", "related", "cross_role"}, "Missing relationship for job")
    return {"resumes": len(resumes), "jobs": len(jobs), "sources": len(sources),
            "labeled_pairs": len(pairs), "requirement_labels": sum(statuses.values()),
            "evidence_status_counts": dict(statuses), "families": sorted(FAMILIES),
            "scoring_executed": False, "independent_semantic_review": False}


def verify_hashes(folder: Path, manifest: dict) -> None:
    require(set(manifest["files"]) == set(PAYLOADS), "Payload hash inventory incomplete")
    for name, expected in manifest["files"].items():
        require(hashlib.sha256((folder / name).read_bytes()).hexdigest() == expected,
                f"Frozen file changed: {name}; version and review dataset deliberately")


def legacy_inventory() -> dict:
    """Inspect old data without importing modules or executing a scorer."""
    benchmark = ROOT / "benchmarks"
    module = ast.parse((benchmark / "independent_resumes.py").read_text())
    independent = next(ast.literal_eval(n.value) for n in module.body
                       if isinstance(n, ast.Assign) and any(
                           isinstance(t, ast.Name) and t.id == "RESUMES" for t in n.targets))
    new_resumes = json.loads((benchmark / "holdout/synthetic_resumes.json").read_text())
    jobs = json.loads((benchmark / "jobs.json").read_text())
    new_jobs = json.loads((benchmark / "holdout/new_public_jobs.json").read_text())
    example_resume = (ROOT / "examples/synthetic_resume.txt").read_text()
    example_job = (ROOT / "examples/truey_job.txt").read_text()
    def words(items):
        counts = [len(x.split()) for x in items]
        return {"count": len(counts), "min_words": min(counts), "max_words": max(counts)}
    return {"calibration_resumes": words(independent.values()),
            "additional_resumes": words(new_resumes.values()),
            "calibration_job_briefs": words(x["description"] for x in jobs),
            "additional_job_briefs": words(x["jd"] for x in new_jobs.values()),
            "example_resume": words([example_resume]), "example_job": words([example_job]),
            "observed_external_pairs": len(json.loads((benchmark / "independent_results.json").read_text())["cases"]),
            "normalized_exact_resume_duplicates": len(independent) + len(new_resumes) + 1
                - len({normalized(x) for x in [*independent.values(), *new_resumes.values(), example_resume]})}


if __name__ == "__main__":
    data = load_corpus()
    verify_hashes(CORPUS, data["manifest"])
    print(json.dumps({"new_corpus": validate(data), "existing_data": legacy_inventory()}, indent=2))
