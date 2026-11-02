"""Upplai-like public request/response shape and stateful job ID semantics.

In-memory session caching is for a single-user local development server.
It is NOT safe as an unauthenticated multitenant persistence layer.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from threading import Lock
from typing import Any
from .engine import score_resume

MAX_AGE_SECONDS = 60 * 60
MAX_SESSIONS = 100


@dataclass
class Session:
    resume: str = ""
    job_descriptions: dict[str, str] = field(default_factory=dict)
    updated: float = field(default_factory=time.monotonic)


class ATSService:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = Lock()

    def analyze(self, resume_text: str | None = None, job_description: str | None = None,
                job_description_id: str | None = None, session_id: str = "local",
                mode: str = "compatibility") -> dict[str, Any]:
        session_id = session_id.strip()
        if not 1 <= len(session_id) <= 128:
            raise ValueError("session_id must have 1–128 characters")
        if job_description and job_description_id:
            raise ValueError("Supply job_description OR job_description_id, not both")
        # Validate incoming strings before changing cached session state.
        if resume_text is not None and len(''.join(resume_text.split())) < 100:
            raise ValueError("A complete resume (at least 100 non-whitespace characters) is required")
        if job_description is not None and len(''.join(job_description.split())) < 50:
            raise ValueError("A complete job description (at least 50 non-whitespace characters) is required")
        if not job_description and not job_description_id:
            raise ValueError("Supply a full job description or an existing job_description_id")

        with self._lock:
            now = time.monotonic()
            for sid in list(self._sessions):
                if now - self._sessions[sid].updated > MAX_AGE_SECONDS:
                    del self._sessions[sid]
            if session_id not in self._sessions and len(self._sessions) >= MAX_SESSIONS:
                oldest = min(self._sessions, key=lambda x: self._sessions[x].updated)
                del self._sessions[oldest]
            session = self._sessions.setdefault(session_id, Session())
            session.updated = now
            if resume_text is not None:
                if not resume_text.strip():
                    raise ValueError("resume_text cannot be blank")
                session.resume = resume_text
            if not session.resume:
                raise ValueError("For the first request, resume_text is required")
            if job_description_id is not None:
                jd = session.job_descriptions.get(job_description_id)
                if jd is None:
                    raise ValueError("Unknown or expired job_description_id for this session")
                result_id = job_description_id
            else:
                if not job_description or not job_description.strip():
                    raise ValueError("job_description cannot be blank")
                jd = job_description
                result_id = str(uuid.uuid4())
                session.job_descriptions[result_id] = jd
            saved_resume = session.resume

        result = score_resume(saved_resume, jd, mode=mode)
        result["id"] = str(uuid.uuid4())
        result["job_description_id"] = result_id
        result["content"] = format_report(result)
        return result


def format_report(result: dict[str, Any]) -> str:
    c = result["keyword_coverage"]
    lines = [f"## ATS Analysis Complete", f"Overall Score: {result['overall_score']}%",
             f"Job Description ID: {result['job_description_id']}",
             f"Keywords present: {c['matched']} out of {c['total']}", "",
             "### Keyword analysis"]
    for k in result["keywords"]:
        lines.append(f"- {k['keyword']}: {'present' if k['present'] else 'missing'}; "
                     f"importance={k['importance']}; score={k['score']}/100")
    details = result.get("details", {})
    assessments = details.get("keyword_evidence", details.get("requirement_weights", []))
    notes = []
    for item in assessments:
        if item.get("status") == "learning_only":
            notes.append(f"- {item['keyword']}: learning only; delivered work is not established.")
        reasons = sorted({e['reason'] for e in item.get('excluded', [])})
        if reasons:
            labels = {'negated': 'explicit denial', 'job_text_overlap': 'overlap with supplied job text',
                      'requirement_prose': 'requirement prose rather than applicant evidence'}
            notes.append(f"- {item['keyword']}: excluded mentions ({'; '.join(labels[r] for r in reasons)}).")
    if notes:
        lines.extend(["", "### Evidence notes", *notes[:12]])
    if result.get("details", {}).get("keyword_stuffing_warnings"):
        lines.extend(["", "### Keyword-stuffing warnings", *
                      ("- " + s for s in result["details"]["keyword_stuffing_warnings"])])
    lines.extend(["", "Experimental heuristic, not Upplai's proprietary implementation or an official ATS score."])
    return "\n".join(lines)


SERVICE = ATSService()
