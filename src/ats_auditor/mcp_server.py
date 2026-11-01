"""ChatGPT/Codex MCP plugin adapter.

Install with `pip install -e '.[mcp]'` then run `ats-auditor-mcp`.
The MCP endpoint is provided by the official Python MCP SDK (typically /mcp).
"""
from __future__ import annotations

import os
import uuid
from .service import SERVICE, ATSService


def create_mcp():
    try:
        from mcp.server.fastmcp import FastMCP
        from mcp.types import CallToolResult, TextContent
    except ImportError as exc:
        raise RuntimeError("MCP SDK missing: pip install -e '.[mcp]'") from exc

    server = FastMCP("ATS Auditor", host=os.environ.get("ATS_HOST", "127.0.0.1"), port=8000,
                     instructions=("Analyze full resumes against complete job descriptions. "
                                   "Explain missing keywords and evidence gaps. "
                                   "Results are estimates, not official hiring decisions. "
                                   "For an updated resume pass resume_text and prior job_description_id."))

    # Health check does not reveal user input and is only exposed on loopback
    # by deploy/compose.yml. The public Caddy proxy only permits /health.
    from starlette.responses import JSONResponse

    @server.custom_route("/health", methods=["GET"])
    async def health(request):
        return JSONResponse({"status": "ok", "service": "ats-auditor-mcp"})

    def score_safely(resume_text, job_description, job_description_id, session_id, scoring_mode) -> CallToolResult:
        """Send both text content and structured data on the MCP wire.

        Chat clients can consume text even if structuredContent is unsupported;
        applications can still read the complete structured scoring fields.
        """

        # Production is deliberately stateless until authenticated tenant identities
        # are available. Avoid sharing a default 'local' session across MCP users.
        if os.environ.get("ATS_DEPLOYMENT_MODE") == "production":
            if resume_text is None or job_description is None or job_description_id:
                raise ValueError("Production requires full resume_text and job_description on every call")
            result = ATSService().analyze(resume_text=resume_text, job_description=job_description,
                                          session_id=str(uuid.uuid4()), mode=scoring_mode)
        else:
            result = SERVICE.analyze(resume_text=resume_text, job_description=job_description,
                                     job_description_id=job_description_id, session_id=session_id, mode=scoring_mode)
        return CallToolResult(
            content=[TextContent(type="text", text=result["content"])],
            structuredContent=result,
        )

    @server.tool()
    def get_resume_ats_score(
        resume_text: str | None = None,
        job_description: str | None = None,
        job_description_id: str | None = None,
        session_id: str = "local",
        scoring_mode: str = "compatibility",
    ) -> CallToolResult:
        """Compare full resume against full JD; give 0–100 score and keyword details.

        First request: resume_text AND job_description.
        Updated resume for prior job: resume_text AND job_description_id (local mode only).
        New job with same resume: job_description only (local mode only).
        In production, resend both full texts each time to prevent cross-user leaks.
        Modes: compatibility (frequency-sensitive) or evidence (anti-stuffing).
        """
        return score_safely(resume_text, job_description, job_description_id, session_id, scoring_mode)

    @server.tool()
    def compare_resume_quality(
        resume_text: str,
        job_description: str,
        session_id: str = "local",
    ) -> CallToolResult:
        """Evidence-oriented ATS match that discounts keyword stuffing and lists gaps."""
        return score_safely(resume_text, job_description, None, session_id, "evidence")
    return server


def main() -> None:
    server = create_mcp()
    server.run(transport="streamable-http")


if __name__ == "__main__":
    main()
