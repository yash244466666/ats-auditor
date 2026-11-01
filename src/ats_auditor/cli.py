"""Local CLI for ATS Auditor."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .service import ATSService


def main() -> None:
    parser = argparse.ArgumentParser(description="Run independent ATS scoring locally")
    parser.add_argument("--resume", type=Path, required=True, help="Full UTF-8 resume text")
    parser.add_argument("--job", type=Path, required=True, help="Full UTF-8 job description")
    parser.add_argument("--mode", choices=["compatibility", "evidence"], default="compatibility")
    parser.add_argument("--json", action="store_true", help="Emit full JSON instead of text")
    args = parser.parse_args()
    svc = ATSService()
    output = svc.analyze(resume_text=args.resume.read_text(encoding="utf-8"),
                         job_description=args.job.read_text(encoding="utf-8"), mode=args.mode)
    print(json.dumps(output, indent=2, ensure_ascii=False) if args.json else output["content"])


if __name__ == "__main__":
    main()
