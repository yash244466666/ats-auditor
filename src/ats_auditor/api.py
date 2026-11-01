"""Self-hosted HTTP API. Add TLS, tenant authentication and quotas for production."""
from __future__ import annotations

import os
from typing import Literal
from fastapi import FastAPI, HTTPException, Header, Depends
import hmac
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel, Field
from .service import SERVICE

app = FastAPI(title="ATS Auditor", version="0.4.0",
              description="Transparent ATS analysis. Not associated with Upplai.")


class ScoreRequest(BaseModel):
    resume_text: str | None = Field(default=None, max_length=100_000)
    job_description: str | None = Field(default=None, max_length=50_000)
    job_description_id: str | None = None
    session_id: str = Field(default="local", min_length=1, max_length=128)
    mode: Literal["compatibility", "evidence", "requirement_fit"] = "compatibility"


def api_auth(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.environ.get("ATS_API_KEY", "")
    if os.environ.get("ATS_DEPLOYMENT_MODE", "development") == "production" and not expected:
        raise HTTPException(status_code=503, detail="Service is not configured securely")
    if expected and (not x_api_key or not hmac.compare_digest(x_api_key, expected)):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ats-auditor"}


@app.post("/v1/get_resume_ats_score", dependencies=[Depends(api_auth)])
@app.post("/v1/score", dependencies=[Depends(api_auth)])
def score(request: ScoreRequest) -> dict:
    try:
        return SERVICE.analyze(**request.model_dump(exclude={"mode"}), mode=request.mode)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
