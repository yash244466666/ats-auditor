# Security Policy

## Supported releases

Security fixes target the current `main` branch. Earlier development releases are provided as-is.

## Reporting vulnerabilities

**Do not file a public issue containing proof-of-concept exploits, sensitive resumes, SSH credentials or secret values.** Instead, use the GitHub repository's private vulnerability reporting feature, if enabled. If it is not enabled, contact the repository maintainer privately through their GitHub profile and request a secure reporting channel. Do not send credentials or applicant data through public discussion threads.

## Deployment warnings

- This repository contains a development HTTP API and an experimental MCP adapter. The server is **not safe for direct public exposure** without an authenticated reverse proxy, tenant isolation and rate limiting.
- The included Caddyfile intentionally returns HTTP 403 for unauthenticated MCP requests. Do not remove this safeguard before OAuth or a verified client-authenticated alternative is implemented and tested.
- The `session_id` parameter is not authentication. No service should trust callers to choose their own tenant identity.
- Use dedicated SSH deployment keys, verified SSH host-key fingerprints, encrypted GitHub Actions secrets, and separate staging/production environments.
- Rotate any credentials ever shared in chats, logs, or issue trackers; never publish them in the repository.

## Disclosure

Allow reasonable time for remediation before public disclosure, and avoid testing against systems you do not own or have explicit authorization to assess.
