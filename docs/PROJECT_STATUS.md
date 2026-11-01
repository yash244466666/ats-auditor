# ATS Auditor — verified project status

**Snapshot:** 2026-11-02 (Asia/Dhaka). This is a dated record, not an automatic health monitor.

## What is working

- **Repository:** [yash244466666/ats-auditor](https://github.com/yash244466666/ats-auditor), open-source MIT project. The Python scoring engine remains an independent, heuristic approximation; scores are not official employer ATS decisions or guaranteed matches to Upplai.
- **CI:** The `main` commit `d74350bf7fda91b27fb0ab4522ea34684d59026f` passed [CI run 41349223958](https://github.com/yash244466666/ats-auditor/actions/runs/41349223958); Python 3.11, 3.12, 3.13 and Docker jobs were successful. The `dev` pipeline also passed [run 41349063702](https://github.com/yash244466666/ats-auditor/actions/runs/41349063702).
- **Deployment:** [Production deployment run 41349261322](https://github.com/yash244466666/ats-auditor/actions/runs/41349261322) successfully shipped that `main` commit to the VPS. The server-side gate checks the loopback health endpoint before reporting success.
- **MCP transport:** Production runs the MCP SDK's Streamable HTTP server behind Caddy at `https://atsmcp.yashcodes.com/mcp`, with `/health` proxied to production. The public URL was not independently verified by a separate HTTP probe for this snapshot, but the ChatGPT-connected MCP tools **did** return real scoring results in a live conversation.
- **End-to-end tool calls:** Both `get_resume_ats_score` and `compare_resume_quality` returned populated `structuredContent` in ChatGPT with fictional test inputs; the scores in that one illustrative test were **22** (compatibility) and **35** (evidence). These sample scores do not represent accuracy or production performance.
- **MCP response fix:** [PR #11](https://github.com/yash244466666/ats-auditor/pull/11) merged `CallToolResult` responses with both a human-readable `TextContent` report and full structured score data. Automated MCP client/server regression tests now call both tools and assert that the results are nonempty.
- **Deployment identity:** GitHub Actions uses `VPS_SSH_KEY` and `VPS_SSH_KNOWN_HOSTS` with the dedicated `atsdeploy` forced-command SSH gate. The earlier password-based GitHub deployment approach was superseded. Production and staging map to VPS loopback ports `8800` and `8801`; deploy builds are serialized for the resource-constrained host.
- **Branch workflow:** `dev` for development/staging; protected `main` for production after CI and pull-request review/merge. `scripts/sync-branches.sh` supports synchronizing `dev` after a production release.

## Security state — known outstanding work

**Authentication and authorization are intentionally deferred.** At the time of this snapshot, the public `/mcp` route is **not authenticated**. The production scoring mode is stateless and requires a full resume and job description on every request; this reduces cross-caller session sharing but **does not** provide authentication, access control, privacy guarantees, or abuse protection.

**Do not submit real applicant resumes, confidential job descriptions, credentials, or other sensitive data to this public endpoint while authentication is absent.** The 2 MB request-body limit and TLS reverse proxy are not substitutes for identity, quotas, or tenant isolation.

### Deferred priorities

1. Add supported OAuth 2.1 or another verified, ChatGPT-compatible authentication mechanism and authorization/tenant isolation.
2. Add rate limiting, request sizing/abuse controls, privacy-safe logging, monitoring and rollback practices.
3. Verify authentication and isolation before using real applicant data; maintain end-to-end scoring tests in CI.
4. Validate scoring quality with an untouched, consented holdout dataset instead of treating calibration scores as official ATS truth.

## Documentation pointers

- [Project README](../README.md): scoring modes and local or MCP usage.
- [VPS deployment](../deploy/README.md): SSH gate, CI/CD, Caddy and ports.
- [Security policy](../SECURITY.md): current unauthenticated-exposure warning.
- [Benchmark limitations](../benchmarks/INDEPENDENT_VALIDATION.md): observed error and research caveats.

**Maintenance:** When a milestone changes, update this dated record, `README.md`, `deploy/README.md`, and `SECURITY.md` together, and verify the latest CI/CD runs before claiming deployment success.
