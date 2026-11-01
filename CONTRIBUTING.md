# Contributing to ATS Auditor

Thank you for helping improve an independent, open-source resume–job matching project.

## Development

1. Fork the repository and branch from `dev` for your change.
2. Use Python 3.11 or newer and install `python -m pip install -e '.[dev]'`.
3. Run `pytest -q` and `python -m compileall -q src`.
4. Open a pull request into `dev` with a description, test cases, and a clear explanation of any scoring changes. Once verified, maintainers can promote `dev` to `main`.

## Scoring changes

- Use fully synthetic or redistributable test resumes and job descriptions.
- Report scores on **unseen** resume–job pairs separately from scores used for calibration.
- Show sample size, mean absolute error, maximum error, and per-role limitations.
- Keep the *compatibility estimate*, *requirements fit*, and *evidence* scores distinct.
- Explain how keyword extraction, weighting and normalization work; do not claim to reproduce anyone's proprietary algorithm exactly.
- Do not optimize by adding false employment claims or recommending keyword stuffing.

## Privacy and security

Never commit real applicant resumes, personal contact information, access tokens, SSH keys, production `.env` files, server passwords, or customer data. Use `example.test` contacts and fictional organizations in test fixtures.

Please report security vulnerabilities privately as described in [SECURITY.md](SECURITY.md), not through public issues.

## Licensing

By contributing, you agree that your contributions are available under the project's MIT License.
