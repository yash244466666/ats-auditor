# Security Policy

## Supported releases

Security fixes target the current `main` branch. Earlier development releases are provided as-is.

## Reporting vulnerabilities

**Do not file a public issue containing proof-of-concept exploits, sensitive resumes, SSH credentials or secret values.** Instead, use the GitHub repository's private vulnerability reporting feature, if enabled. If it is not enabled, contact the repository maintainer privately through their GitHub profile and request a secure reporting channel. Do not send credentials or applicant data through public discussion threads.

## Deployment warnings

- **Current exposure as of 2026-11-02:** The production Streamable HTTP MCP service is deployed at `https://atsmcp.yashcodes.com/mcp` behind Caddy; the `/mcp` route is **public and unauthenticated**. Authentication has intentionally been deferred. This is **not** ready for confidential applicant data.
- **Do not submit real resumes, personally identifying information, private job descriptions or secrets** to the public MCP endpoint. Use fictional test records until proper access controls are in place.
- The included Caddyfile currently **reverse-proxies `/mcp` and `/mcp/*`**, with a 2 MB request-body cap and TLS. It does **not** return 403 or enforce user authentication. Request-size limits and HTTPS are not substitutes for authorization, rate limiting or abuse prevention.
- Production MCP operates statelessly: callers must send a full resume and full job description with each request; this prevents reuse of a shared default session but **does not** provide user identity, audit security or tenant isolation. The `session_id` parameter is **not** authentication.
- The next security milestone is verified OAuth 2.1 or a supported alternative, user-scoped authorization, tenant isolation, rate limits, monitoring and a privacy review. Do not describe deployment/CI success as completion of these controls.
- GitHub Actions uses a dedicated `atsdeploy` forced-command SSH deployment key with pinned known-host verification. The earlier password-based deploy workflow was superseded. Store secrets in encrypted GitHub Actions secrets; keep staging separate from production.
- Rotate any credentials ever shared in chats, logs or issue trackers; never publish them in the repository.

See [the dated project status](docs/PROJECT_STATUS.md) and [VPS deployment notes](deploy/README.md) for the verified state.

## Disclosure

Allow reasonable time for remediation before public disclosure, and avoid testing against systems you do not own or have explicit authorization to assess.
