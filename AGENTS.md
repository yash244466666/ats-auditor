# AGENTS.md — Entry point for coding agents

**Read [AGENT.md](AGENT.md) in full before acting in this repository.** It is the detailed project context, architecture, safety constraints, source map, testing and release checklist. For Claude Code-specific conventions, also read [CLAUDE.md](CLAUDE.md).

## Non-negotiable defaults

- Read `benchmarks/public_skillspan/README.md` before running the public extraction benchmark. Keep external data in the ignored cache and extraction metrics separate from resume-fit claims; tests use fictional text only.

- Work against the current repository HEAD; treat docs/PROJECT_STATUS.md as a dated record, not a live monitor.
- Make scoped, tested changes on dev/a review branch; open a PR and pass required Python 3.11/3.12/3.13 and Docker checks before **squash-merging** into protected main.
- Distinguish experimental ATS matching scores from hiring decisions and proprietary ATS outputs. Never fabricate experience or benchmark accuracy.
- Use **fictional** resumes and job postings in tests, demos and live MCP smoke calls. The public production /mcp endpoint currently has **no authentication**; its future implementation is deferred, not optional for sensitive data.
- Preserve production MCP's stateless full-resume/full-job requirement and both text and structured tool responses; don't regress the prior empty-response bug.
- Never expose SSH private keys, passwords, GitHub secrets or applicant data in commits, logs or chat.
- Confirm changes with actual tests, CI run IDs and deployment evidence; don't claim unverified success.

See [README.md](README.md), [SECURITY.md](SECURITY.md), [CONTRIBUTING.md](CONTRIBUTING.md), [deploy/README.md](deploy/README.md) and [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for source-backed details.
